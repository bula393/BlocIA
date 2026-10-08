import json

import httpx
import pytest

from app.application.chat import ai_responder, free_models, inference_client as transport, local_models
from app.application.chat.ai_responder import AIResponseUnavailableError
from app.application.chat.local_models import ModelUnavailableError


CLASSIFICATION = {"label": "no_personal", "group": "no_personal", "confidence": 0.9,
                  "status": "aceptada", "needs_human_review": False}
MODEL = {"providerId": "local", "modelId": "qwen3-local", "displayName": "Qwen local"}
STATUS = {"ready": True, "classifierReady": True, "mode": "classification", "freeModels": [MODEL]}


def test_remote_transport_sends_private_token_body_and_per_operation_timeouts(monkeypatch):
    monkeypatch.setenv("BLOCIA_INFERENCE_TIMEOUT_SECONDS", "180")
    requests = []

    def reply(request):
        requests.append(request)
        payload = CLASSIFICATION if request.url.path == "/classify" else {"answer": " Respuesta "} if request.url.path == "/generate" else STATUS
        return httpx.Response(200, json=payload, headers={"set-cookie": "session=private; Path=/"})

    with httpx.Client(transport=httpx.MockTransport(reply)) as client:
        remote = transport.InferenceClient("http://inference:8001", "private-token", client)
        assert remote.classify("private-prompt") == CLASSIFICATION
        assert remote.generate("context + private-prompt") == "Respuesta"
        assert remote.status() == STATUS
        remote.warmup()
        remote.warmup(include_generation=True)
    assert all(request.headers["x-inference-token"] == "private-token" for request in requests)
    assert all("cookie" not in request.headers for request in requests)
    assert all("private-token" not in str(request.url) and "private-prompt" not in str(request.url) for request in requests)
    assert json.loads(requests[0].content) == {"prompt": "private-prompt"}
    assert json.loads(requests[1].content) == {"prompt": "context + private-prompt", "modelId": "qwen3-local"}
    assert json.loads(requests[3].content) == {"includeGeneration": False}
    assert [request.extensions["timeout"]["read"] for request in requests] == [30, 180, 30, 30, 180]
    assert all(request.extensions["timeout"]["connect"] == 5 for request in requests)


@pytest.mark.parametrize("failure", ["unavailable", "unauthorized", "timeout", "bad_json", "bad_schema"])
def test_remote_failures_are_safe_and_map_to_existing_domain_errors(failure, caplog):
    def reply(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("private-prompt private-token", request=request)
        if failure in {"unavailable", "unauthorized"}:
            return httpx.Response(503 if failure == "unavailable" else 401, json={"detail": "private-prompt private-token"})
        if failure == "bad_json":
            return httpx.Response(200, content="private-prompt private-token")
        return httpx.Response(200, json={"label": "private-prompt", "answer": None})

    with httpx.Client(transport=httpx.MockTransport(reply)) as client:
        remote = transport.InferenceClient("http://inference:8001", "private-token", client)
        with pytest.raises(ModelUnavailableError) as classification_error:
            remote.classify("private-prompt")
        with pytest.raises(AIResponseUnavailableError) as generation_error:
            remote.generate("private-prompt")
        status = remote.status()
        assert status["ready"] is False and status["classifierReady"] is False
        assert status["freeModels"] == [] and status["inferenceAvailable"] is False
    for error in [classification_error.value, generation_error.value]:
        assert "private-prompt" not in str(error) and "private-token" not in str(error)
        assert error.__suppress_context__ is True
    assert "private-prompt" not in caplog.text and "private-token" not in caplog.text


@pytest.mark.parametrize("value", [None, "", "invalid", "0", "-3", "nan", "inf"])
def test_invalid_generation_timeout_uses_default(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("BLOCIA_INFERENCE_TIMEOUT_SECONDS", raising=False)
    else:
        monkeypatch.setenv("BLOCIA_INFERENCE_TIMEOUT_SECONDS", value)
    assert transport.generation_timeout_seconds() == 300


def test_local_and_remote_factories_keep_existing_interfaces(monkeypatch):
    local_models.local_models.cache_clear()
    ai_responder.local_text_model.cache_clear()
    monkeypatch.delenv("BLOCIA_INFERENCE_URL", raising=False)
    try:
        assert isinstance(local_models.local_models(), local_models.LocalModels)
        assert isinstance(ai_responder.local_text_model(), ai_responder.LocalTextModel)
        local_models.local_models.cache_clear()
        ai_responder.local_text_model.cache_clear()
        monkeypatch.setenv("BLOCIA_INFERENCE_URL", "http://inference:8001")
        remote = transport.InferenceClient("http://inference:8001", "private-token")
        monkeypatch.setattr(transport, "inference_client", lambda: remote)
        assert local_models.local_models() is remote
        assert isinstance(ai_responder.local_text_model(), transport.RemoteTextModel)
        assert ai_responder.local_text_model()._client is remote
        assert remote._client is None
    finally:
        local_models.local_models.cache_clear()
        ai_responder.local_text_model.cache_clear()


def test_remote_local_inventory_does_not_check_models_on_api_machine(monkeypatch):
    monkeypatch.setenv("BLOCIA_INFERENCE_URL", "http://inference:8001")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=STATUS))) as client:
        remote = transport.InferenceClient("http://inference:8001", "private-token", client)
        monkeypatch.setattr(transport, "inference_client", lambda: remote)
        assert free_models.local_free_models() == [MODEL]


def test_shared_client_closes_without_breaking_cached_factory_references(monkeypatch):
    transport.inference_client.cache_clear()
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=STATUS)))
    remote = transport.InferenceClient("http://inference:8001", "private-token", client)
    monkeypatch.setattr(transport, "InferenceClient", lambda: remote)
    try:
        assert transport.inference_client() is remote
        transport.close_inference_client()
        assert client.is_closed and remote._client is None
        assert transport.inference_client() is remote
    finally:
        transport.inference_client.cache_clear()


def test_production_remote_client_requires_private_token(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("BLOCIA_INFERENCE_TOKEN", raising=False)
    with pytest.raises(ValueError, match="BLOCIA_INFERENCE_TOKEN"):
        transport.InferenceClient("http://inference:8001")


@pytest.mark.parametrize("url", ["ftp://inference", "http://user:secret@inference", "http://inference?token=secret", "http://inference#secret", "inference", "http://inference:secret", "http://["])
def test_remote_client_rejects_credential_bearing_or_unsupported_urls(url):
    with pytest.raises(ValueError) as error:
        transport.InferenceClient(url, "private-token")
    assert "secret" not in str(error.value) and "private-token" not in str(error.value)
