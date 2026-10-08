import json
import sys
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import numpy as np
import pytest

from app.application.chat import local_models as runtime
from app.application.chat.settings import ChatSettings, ClassifierSettings


@pytest.fixture
def classifier(monkeypatch, tmp_path):
    artifacts = tmp_path / "ml/artifacts"
    artifacts.mkdir(parents=True)
    embeddings = tmp_path / "models/embeddings"
    embeddings.mkdir(parents=True)
    (embeddings / "model.safetensors").touch()
    manifest = {"embeddings": {"model": "test-encoder", "revision": "test"}}
    (tmp_path / "models/manifest.json").write_text(json.dumps(manifest))
    report = {"passed": True, "encoder": manifest["embeddings"]}
    (artifacts / "training-report.json").write_text(json.dumps(report))
    weights = {"embedding_model": "test-encoder", "prefix": "query: ",
               "classes": ["no_personal", "personal_decision", "personal_informativa"],
               "coef": [[3, 0], [0, 3], [-1, -1]], "intercept": [0, 0, 0]}
    (artifacts / "classifier.json").write_text(json.dumps(weights))
    config = ClassifierSettings(embedding_model="test-encoder", embedding_prefix_query="query: ",
                                labels=weights["classes"], primary_grouping={label: label for label in weights["classes"]},
                                confidence_threshold=0.7, review_threshold=0.55)
    chat_config = ChatSettings(max_input_characters=4000, cpu_threads=4, sensitive_patterns=["medicación"])

    class Tokenizer:
        def encode(self, text, **kwargs):
            return text.split()

        def batch_decode(self, batches, **kwargs):
            return [" ".join(batch) for batch in batches]

    class Encoder:
        loads = 0

        def __init__(self, *args, **kwargs):
            type(self).loads += 1
            self.tokenizer = Tokenizer()
            self.calls = 0

        def encode(self, texts, **kwargs):
            self.calls += 1
            return np.array([[0, 1] if "medicación" in text else [1, 0] for text in texts])

    monkeypatch.setattr(runtime, "ROOT", tmp_path)
    monkeypatch.setattr(runtime, "settings", lambda: (config, chat_config))
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(set_num_threads=lambda threads: None))
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=Encoder))
    return runtime.LocalModels(), artifacts, weights, config, Encoder


def test_repeat_and_concurrent_questions_reuse_inference_without_exposing_mutable_results(classifier):
    models, _, _, _, _ = classifier
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(models.classify, ["¿Qué es una API?"] * 8))
    assert all(result == results[0] for result in results)
    assert models.encoder.calls == 1
    results[0]["probabilities"]["no_personal"] = 0
    assert models.classify("¿Qué es una API?")["probabilities"]["no_personal"] > 0.9


def test_changed_weights_invalidate_results_without_reloading_encoder(classifier):
    models, artifacts, weights, _, encoder = classifier
    assert models.classify("Consulta")["label"] == "no_personal"
    weights["intercept"] = [0, 20, 0]
    (artifacts / "classifier.json").write_text(json.dumps(weights))
    assert models.classify("Consulta")["label"] == "personal_decision"
    assert models.encoder.calls == 2
    assert encoder.loads == 1


def test_failed_training_gate_never_serves_cached_classification(classifier):
    models, artifacts, _, _, _ = classifier
    models.classify("Consulta")
    (artifacts / "training-report.json").write_text('{"passed": false}')
    with pytest.raises(runtime.ModelUnavailableError):
        models.classify("Consulta")


def test_long_prompt_keeps_a_sensitive_decision_at_its_end(classifier):
    models, _, _, _, _ = classifier
    result = models.classify("información " * 650 + "¿debería suspender mi medicación?")
    assert result["chunks"] == 3
    assert result["label"] == "personal_decision"
    assert result["sensitive_decision"] is True
    assert result["needs_human_review"] is True


def test_configuration_change_invalidates_cached_review_status(classifier):
    models, _, _, config, _ = classifier
    assert models.classify("Consulta")["status"] == "aceptada"
    config.confidence_threshold = 0.99
    assert models.classify("Consulta")["status"] == "baja_confianza"


def test_cache_is_bounded(classifier):
    models, _, _, _, _ = classifier
    models._cache_size = 2
    for text in ["uno", "dos", "tres", "uno"]:
        models.classify(text)
    assert len(models._results) == 2
    assert models.encoder.calls == 4
