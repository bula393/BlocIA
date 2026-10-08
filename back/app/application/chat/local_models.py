from collections import OrderedDict
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
import os
import re
from threading import RLock

from .settings import ROOT, settings
from .free_models import local_free_models

os.environ.setdefault("HF_HOME", str(ROOT / "models/.cache"))
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

EXPLICIT_CHOICE = re.compile(r"\b(deber[ií]a|tengo que|me conviene|decid[ií]|eleg[ií]|decime si|qu[eé] hago)\b", re.I)


def _file_version(path):
    try:
        stat = path.stat()
        return stat.st_mtime_ns, stat.st_size
    except FileNotFoundError:
        return None


@lru_cache(maxsize=8)
def _metadata(root, report_version, manifest_version):
    report = root / "ml/artifacts/training-report.json"
    manifest = root / "models/manifest.json"
    return (
        json.loads(report.read_text(encoding="utf-8")) if report_version else {},
        json.loads(manifest.read_text(encoding="utf-8")) if manifest_version else {},
    )


class ModelUnavailableError(RuntimeError):
    pass


class LocalModels:
    def __init__(self):
        self._lock = RLock()
        self.encoder = None
        self.weights = None
        self._version = None
        self._encoder_version = None
        self._coefficients = None
        self._intercepts = None
        self._classes = ()
        self._decision_index = None
        # Keep only hashes and results in memory; never cache question text.
        self._results = OrderedDict()
        self._cache_size = 128

    def _classifier_status(self):
        classifier_config, chat_config = settings()
        report, manifest = _metadata(ROOT, _file_version(ROOT / "ml/artifacts/training-report.json"), _file_version(ROOT / "models/manifest.json"))
        embeddings = ROOT / "models/embeddings"
        classifier_ready = (ROOT / "ml/artifacts/classifier.json").is_file() and report.get("passed", False) and ((embeddings / "model.safetensors").is_file() or (embeddings / "pytorch_model.bin").is_file())
        classifier_ready = classifier_ready and manifest.get("embeddings", {}).get("model") == classifier_config.embedding_model and report.get("encoder") == manifest.get("embeddings")
        return {"ready": bool(classifier_ready), "classifierReady": bool(classifier_ready), "mode": "classification", "model": classifier_config.embedding_model,
                "maxInputCharacters": chat_config.max_input_characters,
                "training": {"examples": report.get("examples"), "macroF1": report.get("test", {}).get("macro avg", {}).get("f1-score"), "decisionRecall": report.get("test", {}).get("personal_decision", {}).get("recall")}}

    def status(self):
        return {**self._classifier_status(), "freeModels": local_free_models(remote=False)}

    def _load_classifier(self):
        with self._lock:
            classifier_config, chat_config = settings()
            weight_path = ROOT / "ml/artifacts/classifier.json"
            encoder_version = tuple(_file_version(ROOT / "models/embeddings" / filename) for filename in (
                "model.safetensors", "pytorch_model.bin", "config.json", "tokenizer.json", "sentence_bert_config.json",
            ))
            version = (ROOT, _file_version(weight_path), encoder_version,
                       _file_version(ROOT / "ml/artifacts/training-report.json"),
                       _file_version(ROOT / "models/manifest.json"),
                       classifier_config.model_dump_json(), chat_config.model_dump_json())
            if self.encoder is not None and self._version == version:
                return
            if not self._classifier_status()["classifierReady"]:
                raise ModelUnavailableError("El clasificador local todavía no está entrenado o no aprobó la evaluación.")
            import numpy as np
            import torch
            from sentence_transformers import SentenceTransformer
            torch.set_num_threads(chat_config.cpu_threads)
            weights = json.loads(weight_path.read_text(encoding="utf-8"))
            if weights["embedding_model"] != classifier_config.embedding_model or weights["prefix"] != classifier_config.embedding_prefix_query:
                raise ModelUnavailableError("La configuración del clasificador cambió: volvé a entrenarlo.")
            if self.encoder is None or self._encoder_version != (ROOT, encoder_version):
                self.encoder = SentenceTransformer(str(ROOT / "models/embeddings"), device="cpu", local_files_only=True, trust_remote_code=False)
                self._encoder_version = (ROOT, encoder_version)
            self.weights = weights
            self._coefficients = np.asarray(weights["coef"], dtype=np.float64).T.copy()
            self._intercepts = np.asarray(weights["intercept"], dtype=np.float64)
            self._classes = tuple(weights["classes"])
            self._decision_index = self._classes.index("personal_decision")
            self._sensitive_patterns = tuple(re.compile(pattern, re.I) for pattern in chat_config.sensitive_patterns)
            self._results.clear()
            self._version = version

    def warmup(self):
        # Load and run the encoder before the first real message arrives.
        self.classify("Consulta de preparación del clasificador.")

    def classify(self, text):
        import numpy as np
        with self._lock:
            self._load_classifier()
            classifier_config, _ = settings()
            cache_key = hashlib.sha256(text.encode("utf-8")).digest()
            cached = self._results.get(cache_key)
            if cached is not None:
                self._results.move_to_end(cache_key)
                return deepcopy(cached)
            # Window over long prompts rather than silently ignoring their ending.
            tokens = self.encoder.tokenizer.encode(text, add_special_tokens=False)
            chunks = self.encoder.tokenizer.batch_decode([tokens[start:start + 360] for start in range(0, len(tokens), 300)], skip_special_tokens=True)
            if not chunks:
                raise ValueError("Escribí una consulta antes de enviarla.")
            features = self.encoder.encode([classifier_config.embedding_prefix_query + chunk for chunk in chunks], normalize_embeddings=True, show_progress_bar=False)
            logits = features @ self._coefficients + self._intercepts
            logits -= logits.max(axis=1, keepdims=True)
            scores = np.exp(logits)
            scores /= scores.sum(axis=1, keepdims=True)
            probabilities = scores.mean(axis=0)
            decision_chunk = int(scores[:, self._decision_index].argmax())
            if scores[decision_chunk, self._decision_index] >= classifier_config.confidence_threshold:
                probabilities = scores[decision_chunk]
            index = int(probabilities.argmax())
            label = self._classes[index]
            confidence = float(probabilities[index])
            status = "revision_manual" if confidence < classifier_config.review_threshold else "baja_confianza" if confidence < classifier_config.confidence_threshold else "aceptada"
            sensitive = any(pattern.search(text) for pattern in self._sensitive_patterns)
            explicit_choice = bool(EXPLICIT_CHOICE.search(text))
            result = {"label": label, "group": classifier_config.primary_grouping[label], "confidence": round(confidence, 4), "status": status,
                      "needs_human_review": status == "revision_manual" or (sensitive and (label == "personal_decision" or explicit_choice)),
                      "sensitive_decision": bool(sensitive and (label == "personal_decision" or explicit_choice)),
                      "probabilities": {key: round(float(value), 4) for key, value in zip(self._classes, probabilities)}, "chunks": len(chunks)}
            self._results[cache_key] = result
            if len(self._results) > self._cache_size:
                self._results.popitem(last=False)
            return deepcopy(result)


@lru_cache(maxsize=1)
def local_models():
    from .inference_client import inference_client, inference_url
    if inference_url():
        return inference_client()
    return LocalModels()
