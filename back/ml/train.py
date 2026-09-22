"""Train on the supplied Markdown; evaluate held-out groups before publishing weights."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HOME", str(ROOT / "models/.cache"))
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


def normalized(text):
    return " ".join(re.findall(r"\w+", "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))))


def extract_examples(source, labels):
    examples = {}
    for line in source.splitlines():
        if "|" not in line:
            continue
        text, label = line.rsplit("|", 1)
        label = label.strip()
        text = re.sub(r"^\d+\.\s*", "", text.strip())
        if label not in labels or not text:
            continue
        key = normalized(text)
        if key in examples and examples[key]["label"] != label:
            raise ValueError(f"Contradictory labels for: {text}")
        examples[key] = {"text": text, "label": label}
    if any(count < 30 for count in Counter(row["label"] for row in examples.values()).values()):
        raise ValueError("At least 30 examples per label are required")
    if set(row["label"] for row in examples.values()) != set(labels):
        raise ValueError("The dataset must contain all configured labels")
    return list(examples.values())


def duplicate_groups(texts):
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectors = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit_transform([normalized(t) for t in texts])
    similarity = (vectors @ vectors.T).toarray()
    parent = list(range(len(texts)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for left, right in zip(*np.where(np.triu(similarity, 1) >= 0.78)):
        parent[root(int(right))] = root(int(left))
    return np.array([root(i) for i in range(len(texts))])


def main():
    import numpy as np
    import torch
    import yaml
    from sentence_transformers import SentenceTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix, f1_score
    from sklearn.model_selection import StratifiedGroupKFold

    torch.set_num_threads(4)
    config = yaml.safe_load((ROOT / "config/classifier.yaml").read_text(encoding="utf-8"))
    source = (ROOT / "ml/source/datos_entrenamiento_clasificador_preguntas.md").read_text(encoding="utf-8")
    rows = extract_examples(source, config["labels"])
    artifact_dir = ROOT / "ml/artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "ml/dataset.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    texts = [row["text"] for row in rows]
    labels = np.array([row["label"] for row in rows])
    groups = duplicate_groups(texts)
    splitter = StratifiedGroupKFold(n_splits=round(1 / config["test_size"]), shuffle=True, random_state=config["random_state"])
    development, test = next(splitter.split(texts, labels, groups))
    validation_folds = round((1 - config["test_size"]) / config["validation_size"])
    splitter = StratifiedGroupKFold(n_splits=validation_folds, shuffle=True, random_state=config["random_state"])
    train_part, validation_part = next(splitter.split(development, labels[development], groups[development]))
    train, validation = development[train_part], development[validation_part]
    assert not (set(groups[train]) & set(groups[test]) or set(groups[train]) & set(groups[validation]) or set(groups[test]) & set(groups[validation]))
    print(f"Examples: {len(rows)}. Train/validation/test: {len(train)}/{len(validation)}/{len(test)}", flush=True)
    encoder = SentenceTransformer(str(ROOT / "models/embeddings"), device="cpu", local_files_only=True, trust_remote_code=False)
    features = encoder.encode([config["embedding_prefix_query"] + text for text in texts], normalize_embeddings=True, batch_size=16, show_progress_bar=True)
    candidates = []
    for regularization in [0.1, 1.0, 10.0, 100.0]:
        model = LogisticRegression(C=regularization, max_iter=config["max_iter"], class_weight=config["class_weight"], random_state=config["random_state"])
        model.fit(features[train], labels[train])
        score = f1_score(labels[validation], model.predict(features[validation]), average="macro", zero_division=0)
        candidates.append((float(score), regularization, model))
    best_score, chosen_c, model = max(candidates, key=lambda item: (item[0], -item[1]))
    predictions = model.predict(features[test])
    metrics = classification_report(labels[test], predictions, labels=config["labels"], output_dict=True, zero_division=0)
    gate = config["quality_gate"]
    passed = metrics["macro avg"]["f1-score"] >= gate["macro_f1"] and metrics["personal_decision"]["recall"] >= gate["personal_decision_recall"]
    manifest = json.loads((ROOT / "models/manifest.json").read_text(encoding="utf-8"))
    report = {
        "trained_at": datetime.now(timezone.utc).isoformat(), "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "examples": len(rows), "counts": dict(Counter(labels)), "near_duplicate_groups": len(set(groups)),
        "split": {name: {"count": len(indexes), "counts": dict(Counter(labels[indexes])), "indexes": indexes.tolist()} for name, indexes in [("train", train), ("validation", validation), ("test", test)]},
        "selection": {"C": chosen_c, "validation_macro_f1": best_score, "candidates": [{"C": c, "validation_macro_f1": score} for score, c, _ in candidates]},
        "test": metrics, "confusion_matrix": confusion_matrix(labels[test], predictions, labels=config["labels"]).tolist(),
        "label_order": config["labels"], "quality_gate": gate, "passed": bool(passed), "encoder": manifest["embeddings"],
        "limitations": "Evaluation on synthetic examples supplied by the user, grouped by lexical similarity. It does not establish accuracy on real-world queries or eliminate semantic overlap.",
    }
    (artifact_dir / "training-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(classification_report(labels[test], predictions, zero_division=0), flush=True)
    if not passed:
        raise SystemExit("Quality gate failed. The classifier was not published; review the dataset and report.")
    weights = {"classes": model.classes_.tolist(), "coef": model.coef_.tolist(), "intercept": model.intercept_.tolist(),
               "embedding_model": config["embedding_model"], "prefix": config["embedding_prefix_query"], "encoder": manifest["embeddings"],
               "source_sha256": report["source_sha256"], "trained_at": report["trained_at"]}
    temporary = artifact_dir / "classifier.tmp"
    temporary.write_text(json.dumps(weights, ensure_ascii=False), encoding="utf-8")
    temporary.replace(artifact_dir / "classifier.json")
    print("Quality gate passed. Local classifier published.", flush=True)


if __name__ == "__main__":
    main()
