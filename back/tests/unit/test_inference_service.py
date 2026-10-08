from types import SimpleNamespace
import json
import sys

from fastapi.testclient import TestClient
import pytest

from app import inference_main
from app.application.chat import free_models, local_models
from app.application.chat.ai_responder import LocalTextModel
from ml import prepare


class FakeClassifier:
    ready = True
    calls = None
    warmed = 0

    def status(self):
        return {"ready": self.ready, "classifierReady": self.ready, "mode": "classification", "freeModels": []}

    def classify(self, prompt):
        self.calls = prompt
        return {"label": "no_personal", "group": "no_personal", "confidence": 0.9,
                "status": "aceptada", "needs_human_review": False}

    def warmup(self):
        self.warmed += 1


class FakeGenerator:
    calls = None
    warmed = 0

    def generate(self, prompt):
        self.calls = prompt
        return "Respuesta"

    def warmup(self):
        self.warmed += 1


@pytest.fixture
def inference(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("BLOCIA_INFERENCE_TOKEN", "private-token")
    monkeypatch.setenv("BLOCIA_PRELOAD_CLASSIFIER", "0")
    monkeypatch.setenv("BLOCIA_PRELOAD_LOCAL_CHAT", "0")
    monkeypatch.setenv("BLOCIA_ENABLE_LOCAL_CHAT", "1")
    classifier, generator = FakeClassifier(), FakeGenerator()
    with TestClient(inference_main.create_app(classifier, generator)) as client:
        yield client, classifier, generator


def test_health_and_readiness_are_public_and_expose_only_availability(inference):
    client, classifier, _ = inference
    assert client.get("/health").json() == {"ok": True}
    assert client.get("/ready").json() == {"ready": True, "classifierReady": True}
    classifier.ready = False
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"ready": False, "classifierReady": False}
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(("method", "path", "body"), [
    ("GET", "/status", None), ("POST", "/classify", {"prompt": "Consulta"}),
    ("POST", "/generate", {"prompt": "Consulta", "modelId": "qwen3-local"}),
    ("POST", "/warmup", {}),
])
def test_inference_operations_require_configured_private_token(inference, method, path, body):
    client, classifier, generator = inference
    for headers in [{}, {"X-Inference-Token": "wrong-token"}]:
        response = client.request(method, path, json=body, headers=headers)
        assert response.status_code == 401
        assert "private-token" not in response.text
        assert classifier.calls is None and generator.calls is None


def test_classification_generation_and_explicit_warmup(inference):
    client, classifier, generator = inference
    headers = {"X-Inference-Token": "private-token"}
    assert client.get("/status", headers=headers).json()["classifierReady"] is True
    response = client.post("/classify", json={"prompt": "Consulta"}, headers=headers)
    assert response.json()["label"] == "no_personal"
    assert classifier.calls == "Consulta"
    response = client.post("/generate", json={"prompt": "Contexto + consulta", "modelId": "qwen3-local"}, headers=headers)
    assert response.json() == {"answer": "Respuesta"}
    assert generator.calls == "Contexto + consulta"
    assert client.post("/warmup", headers=headers).status_code == 200
    assert classifier.warmed == 1 and generator.warmed == 0
    assert client.post("/warmup", json={"includeGeneration": True}, headers=headers).status_code == 200
    assert classifier.warmed == 2 and generator.warmed == 1


@pytest.mark.parametrize(("path", "payload"), [
    ("/classify", {"prompt": "private-prompt " * 1000}),
    ("/classify", {"prompt": "x" * 4001}),
    ("/classify", {"prompt": " "}),
    ("/generate", {"prompt": "private-prompt", "modelId": "unsupported"}),
    ("/generate", {"prompt": "private-prompt " * 2000}),
    ("/generate", {"prompt": " "}),
    ("/warmup", {"includeGeneration": "private-prompt"}),
])
def test_invalid_requests_do_not_echo_user_input_or_invoke_models(inference, path, payload):
    client, classifier, generator = inference
    response = client.post(path, json=payload, headers={"X-Inference-Token": "private-token"})
    assert response.status_code == 422
    assert "private-prompt" not in response.text
    assert classifier.calls is None and generator.calls is None


def test_generation_limit_accepts_maximum_question_with_full_profile_and_history(inference, monkeypatch):
    from app.application.chat.context import build_model_context
    from app.domain.user.user import User
    from app.application.chat.settings import ChatSettings

    client, _, generator = inference
    monkeypatch.setattr(inference_main, "settings", lambda: (None, ChatSettings(max_input_characters=12000, cpu_threads=1, sensitive_patterns=[])))
    history = []
    for index in range(4):
        history.extend([
            {"role": "user", "content": "x" * 600, "requestId": str(index)},
            {"role": "assistant", "content": "y" * 900, "requestId": str(index), "providerId": "local"},
        ])
    user = User(mail="test@example.com", age=28, profession="z" * 120, display_name="n" * 80)
    context = build_model_context(user, "q" * 12000, history)
    assert 18000 < len(context) <= inference_main.MAX_GENERATION_CHARACTERS
    headers = {"X-Inference-Token": "private-token"}
    assert client.post("/classify", json={"prompt": "q" * 12000}, headers=headers).status_code == 200
    assert client.post("/generate", json={"prompt": context}, headers=headers).status_code == 200
    assert generator.calls == context


@pytest.mark.parametrize("operation", ["classify", "generate", "warmup"])
def test_model_failures_are_sanitized_without_logging_prompts(inference, monkeypatch, caplog, operation):
    client, classifier, generator = inference

    def fail(*args):
        raise RuntimeError("private-prompt private-token")

    monkeypatch.setattr(generator if operation == "generate" else classifier, operation, fail)
    response = client.post("/" + operation, json={"prompt": "private-prompt"} if operation != "warmup" else {},
                           headers={"X-Inference-Token": "private-token"})
    assert response.status_code == 503
    assert "private-prompt" not in response.text and "private-token" not in response.text
    assert "private-prompt" not in caplog.text and "private-token" not in caplog.text


def test_production_requires_token_before_serving_requests(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("BLOCIA_INFERENCE_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BLOCIA_INFERENCE_TOKEN"):
        inference_main.create_app(FakeClassifier(), FakeGenerator())


def test_inference_service_instances_are_local_even_with_remote_url(monkeypatch):
    monkeypatch.setenv("BLOCIA_INFERENCE_URL", "http://inference:8001")
    app = inference_main.create_app()
    assert isinstance(app.state.classifier, local_models.LocalModels)
    assert isinstance(app.state.generator, LocalTextModel)
    # The classifier status explicitly requests local inventory, preventing recursion.
    calls = []
    monkeypatch.setattr(local_models, "local_free_models", lambda **kwargs: calls.append(kwargs) or [])
    app.state.classifier.status()
    assert calls == [{"remote": False}]


def test_classifier_only_service_disables_qwen_even_when_preload_requested(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("BLOCIA_INFERENCE_TOKEN", "private-token")
    monkeypatch.setenv("BLOCIA_ENABLE_LOCAL_CHAT", "0")
    monkeypatch.setenv("BLOCIA_PRELOAD_CLASSIFIER", "1")
    monkeypatch.setenv("BLOCIA_PRELOAD_LOCAL_CHAT", "1")
    classifier, generator = FakeClassifier(), FakeGenerator()
    with TestClient(inference_main.create_app(classifier, generator)) as client:
        headers = {"X-Inference-Token": "private-token"}
        assert classifier.warmed == 1 and generator.warmed == 0
        assert client.post("/generate", json={"prompt": "Consulta"}, headers=headers).status_code == 503
        assert client.post("/warmup", json={"includeGeneration": True}, headers=headers).status_code == 503
        assert generator.calls is None
        assert free_models.local_free_models(remote=False) == []


def test_lifespan_warms_direct_models_and_logs_only_failure_type(monkeypatch, caplog):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("BLOCIA_PRELOAD_CLASSIFIER", "1")
    monkeypatch.setenv("BLOCIA_PRELOAD_LOCAL_CHAT", "1")
    monkeypatch.setenv("BLOCIA_ENABLE_LOCAL_CHAT", "1")
    classifier, generator = FakeClassifier(), FakeGenerator()
    with TestClient(inference_main.create_app(classifier, generator)):
        assert classifier.warmed == 1 and generator.warmed == 1

    def fail():
        raise RuntimeError("private-prompt")

    monkeypatch.setattr(classifier, "warmup", fail)
    with TestClient(inference_main.create_app(classifier, generator)) as client:
        assert client.get("/health").status_code == 200
    assert "RuntimeError" in caplog.text and "private-prompt" not in caplog.text


@pytest.mark.parametrize("classifier_only", [False, True])
def test_prepare_downloads_only_requested_models_and_skips_complete_pinned_installations(tmp_path, monkeypatch, classifier_only):
    config = tmp_path / "config"
    config.mkdir()
    (config / "classifier.yaml").write_text("embedding_model: test-encoder\n", encoding="utf-8")
    models_path = tmp_path / "models"
    models_path.mkdir()
    existing_chat = {"model": "existing-chat", "revision": "existing-revision"}
    if classifier_only:
        (models_path / "manifest.json").write_text(json.dumps({"chat": existing_chat}), encoding="utf-8")
    downloaded, looked_up = [], []

    class FakeApi:
        def model_info(self, model_id, revision):
            looked_up.append(model_id)
            return SimpleNamespace(sha=revision, siblings=[SimpleNamespace(rfilename="model.safetensors")])

    def download(model_id, local_dir, **kwargs):
        downloaded.append(model_id)
        local_dir.mkdir(parents=True)
        for filename in ["model.safetensors", "config.json", "tokenizer.json", "modules.json", "1_Pooling/config.json"]:
            path = local_dir / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

    monkeypatch.setattr(prepare, "ROOT", tmp_path)
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(HfApi=FakeApi, snapshot_download=download))
    args = ["--classifier-only"] if classifier_only else []
    prepare.main(args)
    expected = ["test-encoder"] if classifier_only else ["test-encoder", prepare.CHAT_MODEL_ID]
    assert downloaded == expected and looked_up == expected
    manifest = json.loads((tmp_path / "models/manifest.json").read_text(encoding="utf-8"))
    assert manifest["embeddings"] == {"model": "test-encoder", "revision": prepare.EMBEDDING_MODEL_REVISION}
    if classifier_only:
        assert manifest["chat"] == existing_chat
    else:
        assert manifest["chat"]["model"] == prepare.CHAT_MODEL_ID
    prepare.main(args)
    assert downloaded == expected and looked_up == expected


@pytest.mark.parametrize("existing_manifest", [None, {"model": "test-encoder", "revision": "other-revision"}])
def test_prepare_preserves_unverified_or_different_model_revision_until_explicit_replacement(tmp_path, monkeypatch, existing_manifest):
    config = tmp_path / "config"
    config.mkdir()
    (config / "classifier.yaml").write_text("embedding_model: test-encoder\n", encoding="utf-8")
    embeddings = tmp_path / "models/embeddings"
    embeddings.mkdir(parents=True)
    weights = embeddings / "model.safetensors"
    weights.write_bytes(b"existing-weights")
    manifest_path = tmp_path / "models/manifest.json"
    if existing_manifest:
        manifest_path.write_text(json.dumps({"embeddings": existing_manifest}), encoding="utf-8")
    downloads = []

    class FakeApi:
        def model_info(self, model_id, revision):
            return SimpleNamespace(sha=revision, siblings=[SimpleNamespace(rfilename="model.safetensors")])

    monkeypatch.setattr(prepare, "ROOT", tmp_path)
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(
        HfApi=FakeApi, snapshot_download=lambda *args, **kwargs: downloads.append(args[0]),
    ))
    with pytest.raises(RuntimeError, match="Preserving the model volume"):
        prepare.main(["--classifier-only"])
    assert downloads == []
    assert weights.read_bytes() == b"existing-weights"
    assert (json.loads(manifest_path.read_text())["embeddings"] if manifest_path.exists() else None) == existing_manifest
    prepare.main(["--classifier-only", "--force-model-revision"])
    assert downloads == ["test-encoder"]
    assert json.loads(manifest_path.read_text())["embeddings"]["revision"] == prepare.EMBEDDING_MODEL_REVISION
