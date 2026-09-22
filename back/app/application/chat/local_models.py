from functools import lru_cache
import json
import os
import re
from threading import RLock

from .settings import ROOT, settings

os.environ.setdefault("HF_HOME", str(ROOT / "models/.cache"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


class ModelUnavailableError(RuntimeError):
    pass


class LocalModels:
    def __init__(self):
        self._lock = RLock()
        self.encoder = None
        self.weights = None
        self._weights_mtime = None

    def status(self):
        classifier_config, chat_config = settings()
        report_path = ROOT / "ml/artifacts/training-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
        embeddings = ROOT / "models/embeddings"
        manifest_path = ROOT / "models/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        classifier_ready = (ROOT / "ml/artifacts/classifier.json").is_file() and report.get("passed", False) and ((embeddings / "model.safetensors").is_file() or (embeddings / "pytorch_model.bin").is_file())
        classifier_ready = classifier_ready and manifest.get("embeddings", {}).get("model") == classifier_config.embedding_model and report.get("encoder") == manifest.get("embeddings")
        return {"ready": bool(classifier_ready), "classifierReady": bool(classifier_ready), "mode": "classification", "model": classifier_config.embedding_model,
                "maxInputCharacters": chat_config.max_input_characters, "training": {"examples": report.get("examples"), "macroF1": report.get("test", {}).get("macro avg", {}).get("f1-score"), "decisionRecall": report.get("test", {}).get("personal_decision", {}).get("recall")}}

    def _load_classifier(self):
        with self._lock:
            if not self.status()["classifierReady"]:
                raise ModelUnavailableError("El clasificador local todavía no está entrenado o no aprobó la evaluación.")
            classifier_config, chat_config = settings()
            weight_path = ROOT / "ml/artifacts/classifier.json"
            version = weight_path.stat().st_mtime_ns
            if self.encoder is not None and self._weights_mtime == version:
                if self.weights["prefix"] != classifier_config.embedding_prefix_query:
                    raise ModelUnavailableError("El prefijo del clasificador cambió: volvé a entrenarlo.")
                return
            import torch
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(chat_config.cpu_threads)
            weights = json.loads((ROOT / "ml/artifacts/classifier.json").read_text(encoding="utf-8"))
            if weights["embedding_model"] != classifier_config.embedding_model or weights["prefix"] != classifier_config.embedding_prefix_query:
                raise ModelUnavailableError("La configuración del clasificador cambió: volvé a entrenarlo.")
            self.encoder = SentenceTransformer(str(ROOT / "models/embeddings"), device="cpu", local_files_only=True, trust_remote_code=False)
            self.weights = weights
            self._weights_mtime = version

    def classify(self, text):
        import numpy as np
        self._load_classifier()
        classifier_config, chat_config = settings()
        with self._lock:
            # Window over long prompts rather than silently ignoring their ending.
            tokens = self.encoder.tokenizer.encode(text, add_special_tokens=False)
            chunks = [self.encoder.tokenizer.decode(tokens[start:start + 360], skip_special_tokens=True) for start in range(0, len(tokens), 300)]
            if not chunks:
                raise ValueError("Escribí una consulta antes de enviarla.")
            features = self.encoder.encode([classifier_config.embedding_prefix_query + chunk for chunk in chunks], normalize_embeddings=True)
            logits = features @ np.array(self.weights["coef"]).T + np.array(self.weights["intercept"])
        logits -= logits.max(axis=1, keepdims=True)
        scores = np.exp(logits)
        scores /= scores.sum(axis=1, keepdims=True)
        probabilities = scores.mean(axis=0)
        decision_index = self.weights["classes"].index("personal_decision")
        decision_chunk = int(scores[:, decision_index].argmax())
        if scores[decision_chunk, decision_index] >= classifier_config.confidence_threshold:
            probabilities = scores[decision_chunk]
        index = int(probabilities.argmax())
        label = self.weights["classes"][index]
        confidence = float(probabilities[index])
        status = "revision_manual" if confidence < classifier_config.review_threshold else "baja_confianza" if confidence < classifier_config.confidence_threshold else "aceptada"
        sensitive = any(re.search(pattern, text, re.I) for pattern in chat_config.sensitive_patterns)
        explicit_choice = bool(re.search(r"\b(deber[ií]a|tengo que|me conviene|decid[ií]|eleg[ií]|decime si|qu[eé] hago)\b", text, re.I))
        return {"label": label, "group": classifier_config.primary_grouping[label], "confidence": round(confidence, 4), "status": status,
                "needs_human_review": status == "revision_manual" or (sensitive and (label == "personal_decision" or explicit_choice)),
                "sensitive_decision": bool(sensitive and (label == "personal_decision" or explicit_choice)),
                "probabilities": {key: round(float(value), 4) for key, value in zip(self.weights["classes"], probabilities)}, "chunks": len(chunks)}


@lru_cache(maxsize=1)
def local_models():
    return LocalModels()
