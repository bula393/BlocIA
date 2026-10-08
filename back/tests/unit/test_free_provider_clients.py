import io
import json
from urllib.error import HTTPError, URLError
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.application.chat.ai_responder import AIResponder, MODEL_SYSTEM_INSTRUCTION
from app.application.user import list_available_models
from app.application.user.list_available_models import GoogleModelsClient, GroqModelsClient, OpenRouterModelsClient, ProviderModelsUnavailableError
from app.presentation.chat_routes import SendMessage


def test_groq_catalog_uses_own_key_and_excludes_non_chat_models(monkeypatch):
    requests = []

    def respond(request, timeout):
        if request.get_header("User-agent") != "BlocIA/0.1":
            raise HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO(b"error code: 1010"))
        requests.append(request)
        return io.BytesIO(json.dumps({"data": [
            {"id": "llama-3.1-8b-instant", "active": True},
            {"id": "openai/gpt-oss-20b", "active": True},
            {"id": "whisper-large-v3", "active": True},
            {"id": "openai/gpt-oss-safeguard-20b", "active": True},
            {"id": "old-model", "active": False},
        ]}).encode())

    monkeypatch.setattr(list_available_models, "urlopen", respond)

    models = GroqModelsClient().list_models("groq-private-key")

    assert [model.model_id for model in models] == ["llama-3.1-8b-instant", "openai/gpt-oss-20b"]
    assert requests[0].full_url == "https://api.groq.com/openai/v1/models"
    assert requests[0].get_header("Authorization") == "Bearer groq-private-key"


def test_google_catalog_only_offers_models_for_text_chat(monkeypatch):
    items = [
        {"name": "models/gemini-2.5-flash", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-2.5-flash-preview-tts", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-live-native-audio", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-flash-image", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/text-embedding", "supportedGenerationMethods": ["embedContent"]},
    ]
    monkeypatch.setattr(list_available_models, "urlopen", lambda request, timeout: io.BytesIO(json.dumps({"models": items}).encode()))
    assert [model.model_id for model in GoogleModelsClient().list_models("test-key")] == ["gemini-2.5-flash"]


@pytest.mark.parametrize("client", [GoogleModelsClient(), GroqModelsClient()], ids=["google", "groq"])
def test_provider_catalog_explains_outbound_network_block_without_echoing_key(monkeypatch, client):
    def block_request(*args, **kwargs):
        raise URLError(PermissionError("blocked"))

    monkeypatch.setattr(list_available_models, "urlopen", block_request)

    with pytest.raises(ProviderModelsUnavailableError, match="conexión saliente") as error:
        client.list_models("private-provider-key")

    assert "private-provider-key" not in str(error.value)


def test_google_catalog_explains_disabled_service_account_without_echoing_provider_body(monkeypatch):
    def reject(request, timeout):
        body = {"error": {"message": "private-provider-key", "details": [{"reason": "ACCOUNT_STATE_INVALID"}]}}
        raise HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO(json.dumps(body).encode()))

    monkeypatch.setattr(list_available_models, "urlopen", reject)
    with pytest.raises(ProviderModelsUnavailableError, match="ACCOUNT_STATE_INVALID") as error:
        GoogleModelsClient().list_models("private-provider-key")
    assert "cuenta de servicio" in str(error.value)
    assert "private-provider-key" not in str(error.value)


def test_openrouter_catalog_only_returns_zero_price_free_routes(monkeypatch):
    requests = []

    def respond(request, timeout):
        requests.append(request)
        if request.full_url.endswith("/key"):
            return io.BytesIO(json.dumps({"data": {"is_management_key": False, "label": "Mi clave personal"}}).encode())
        return io.BytesIO(json.dumps({"data": [
            {"id": "google/gemini-free:free", "name": "Gemini Free", "pricing": {"prompt": "0", "completion": "0", "request": "0"}, "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]}},
            {"id": "anthropic/claude-paid", "pricing": {"prompt": "0.0001", "completion": "0.0002"}},
            {"id": "example/mispriced:free", "pricing": {"prompt": "0.1", "completion": "0"}},
            {"id": "example/image-only:free", "pricing": {"prompt": "0", "completion": "0"}, "architecture": {"input_modalities": ["text"], "output_modalities": ["image"]}},
        ]}).encode())

    monkeypatch.setattr(list_available_models, "urlopen", respond)

    models = OpenRouterModelsClient().list_models("openrouter-private-key")

    assert [model.model_id for model in models] == ["openrouter/free", "google/gemini-free:free"]
    assert [request.full_url for request in requests] == [
        "https://openrouter.ai/api/v1/key", "https://openrouter.ai/api/v1/models",
    ]
    assert requests[0].get_header("Authorization") == "Bearer openrouter-private-key"
    assert requests[1].get_header("Authorization") == "Bearer openrouter-private-key"


def test_openrouter_does_not_reinsert_router_if_catalog_lists_it_as_paid(monkeypatch):
    def respond(request, timeout):
        if request.full_url.endswith("/key"):
            return io.BytesIO(json.dumps({"data": {"is_management_key": False}}).encode())
        return io.BytesIO(json.dumps({"data": [
            {"id": "openrouter/free", "pricing": {"prompt": "0.01", "completion": "0"}},
        ]}).encode())

    monkeypatch.setattr(
        list_available_models,
        "urlopen",
        respond,
    )

    assert OpenRouterModelsClient().list_models("key") == []


def test_openrouter_rejects_invalid_key_before_public_catalog(monkeypatch):
    requested_urls = []

    def respond(request, timeout):
        requested_urls.append(request.full_url)
        raise HTTPError(request.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"error":{"code":"unauthorized"}}'))

    monkeypatch.setattr(list_available_models, "urlopen", respond)

    with pytest.raises(ProviderModelsUnavailableError, match="no es válida"):
        OpenRouterModelsClient().list_models("invalid-key")
    assert requested_urls == ["https://openrouter.ai/api/v1/key"]


def test_chat_uses_bearer_keys_and_deep_instruction_for_groq_and_openrouter(monkeypatch):
    responder = AIResponder()
    requests = []

    def capture(request, extract, provider_name):
        requests.append(request)
        return "Respuesta"

    monkeypatch.setattr(responder, "_text", capture)

    assert responder.generate("groq", "openai/gpt-oss-20b", "Consulta Groq", "groq-key") == "Respuesta"
    assert responder.generate("openrouter", "openrouter/free", "Consulta Router", "router-key") == "Respuesta"
    assert responder.generate("openrouter", "google/gemini-free:free", "Consulta gratis", "router-key") == "Respuesta"

    assert [request.full_url for request in requests] == [
        "https://api.groq.com/openai/v1/chat/completions",
        "https://openrouter.ai/api/v1/chat/completions",
        "https://openrouter.ai/api/v1/chat/completions",
    ]
    assert [request.get_header("Authorization") for request in requests] == [
        "Bearer groq-key", "Bearer router-key", "Bearer router-key",
    ]
    for request in requests:
        assert json.loads(request.data)["messages"][0] == {"role": "system", "content": MODEL_SYSTEM_INSTRUCTION}
    assert "explicación en profundidad" in MODEL_SYSTEM_INSTRUCTION


def test_paid_openrouter_models_are_rejected_even_in_crafted_chat_requests():
    responder = AIResponder()
    with pytest.raises(ValueError, match="gratuita"):
        responder.generate("openrouter", "anthropic/claude-paid", "Hola", "router-key")
    with pytest.raises(ValidationError, match="gratuita"):
        SendMessage(prompt="Hola", requestId=uuid4(), providerId="openrouter", modelId="anthropic/claude-paid")
