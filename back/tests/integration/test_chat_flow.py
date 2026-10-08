from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from app.application.chat.local_models import local_models, ModelUnavailableError
from app.presentation import chat_routes
from app.infrastructure.database import Database, get_database
from app.infrastructure.chat_repository import ChatRepository, ConversationNotFoundError
from app.main import create_app


class FakeModels:
    fail = False
    calls = 0

    def status(self):
        return {"ready": True}

    def classify(self, prompt):
        self.calls += 1
        if self.fail:
            raise ModelUnavailableError("Modelo temporalmente no disponible")
        return {"label": "no_personal", "group": "no_personal", "confidence": 0.9, "status": "aceptada", "needs_human_review": False}


@pytest.fixture
def sql_chat(tmp_path, monkeypatch):
    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "1440")
    database = Database(tmp_path / "chat.sqlite3")
    models = FakeModels()
    app = create_app()
    app.dependency_overrides[get_database] = lambda: database
    app.dependency_overrides[local_models] = lambda: models
    client = TestClient(app)
    response = client.post("/auth/register", json={"mail": "chat@example.com", "password": "ClaveSegura-123", "age": 24, "profession": "Estudiante"})
    assert response.status_code == 201
    return client, database, models


def test_chat_persists_classification_and_idempotent_retries(sql_chat):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    payload = {"prompt": "¿Qué es una API?", "requestId": str(uuid4())}
    endpoint = f"/chat/conversations/{identifier}/messages"
    first = client.post(endpoint, json=payload)
    assert first.status_code == 200
    assert first.headers["cache-control"] == "no-store"
    assert len(first.json()["messages"]) == 2
    assert not first.json().get("confirmationRequired", False)
    assert first.json()["messages"][1]["classification"]["label"] == "no_personal"
    assert client.post(endpoint, json=payload).json() == first.json()
    assert models.calls == 1
    follow_up = client.post(endpoint, json={"prompt": "Dame un ejemplo", "requestId": str(uuid4())})
    assert follow_up.json()["messages"][-1]["classification"]["label"] == "no_personal"
    assert len(Database(database.path).query("SELECT * FROM messages")) == 4
    assert client.get(f"/chat/conversations/{identifier}").json()["messages"] == follow_up.json()["messages"]
    assert client.get("/health").json()["database"]["ok"]


def test_remote_default_uses_server_key_and_personal_key_takes_priority(sql_chat, monkeypatch):
    from app.domain.user.provider_token import ProviderToken
    from app.infrastructure.user.sqlite_repositories import TokenRepository
    client, database, _ = sql_chat
    monkeypatch.delenv("BLOCIA_DEFAULT_OPENROUTER_TOKEN", raising=False)
    monkeypatch.setenv("BLOCIA_FREE_OPENROUTER_KEY", "server-key")
    monkeypatch.setattr(chat_routes, "default_google_models", lambda: [])
    calls = []

    def generate(self, provider, model, prompt, api_key):
        calls.append(api_key)
        return "Respuesta remota"

    monkeypatch.setattr(chat_routes.AIResponder, "generate", generate)
    status = client.get("/chat/status").json()
    assert status["freeModels"][0]["modelId"] == "openrouter/free"
    assert "server-key" not in str(status)
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    payload = {"prompt": "Hola", "providerId": "openrouter", "modelId": "openrouter/free", "requestId": str(uuid4())}
    response = client.post(endpoint, json=payload)
    assert response.status_code == 200
    assert response.json()["messages"][-1]["content"] == "Respuesta remota"
    tokens = TokenRepository(database)
    tokens.save(ProviderToken.create(str(uuid4()), "chat@example.com", "openrouter", "personal-key"))
    tokens.save_secret("chat@example.com", "openrouter", "personal-key")
    payload["requestId"] = str(uuid4())
    assert client.post(endpoint, json=payload).status_code == 200
    assert calls == ["server-key", "personal-key"]
    payload.update(modelId="anthropic/claude-paid", requestId=str(uuid4()))
    assert client.post(endpoint, json=payload).status_code == 422


@pytest.mark.parametrize("global_key_configured", [True, False])
def test_google_global_key_does_not_advertise_model_from_legacy_credential(sql_chat, monkeypatch, global_key_configured):
    client, _, _ = sql_chat
    if global_key_configured:
        monkeypatch.setenv("BLOCIA_DEFAULT_GOOGLE_TOKEN", "global-google-key")
    else:
        monkeypatch.delenv("BLOCIA_DEFAULT_GOOGLE_TOKEN", raising=False)
    monkeypatch.setattr(chat_routes, "default_google_models", lambda: [{"providerId": "google", "modelId": "legacy-gemini"}])
    monkeypatch.setattr(chat_routes, "google_quota_models", lambda key: {"legacy-gemini"})
    monkeypatch.setattr(chat_routes, "remote_free_models", lambda: [])
    response = client.get("/chat/status")
    assert response.status_code == 200
    expected = [] if global_key_configured else [{"providerId": "google", "modelId": "legacy-gemini"}]
    assert response.json()["freeModels"] == expected
    assert "global-google-key" not in response.text


@pytest.mark.parametrize(("provider_id", "model_id", "environment_variable"), [
    ("google", "gemini-test", "BLOCIA_DEFAULT_GOOGLE_TOKEN"),
    ("groq", "llama-test", "BLOCIA_DEFAULT_GROQ_TOKEN"),
    ("openrouter", "openrouter/free", "BLOCIA_DEFAULT_OPENROUTER_TOKEN"),
    ("openai", "gpt-test", "BLOCIA_DEFAULT_OPENAI_TOKEN"),
    ("anthropic", "claude-test", "BLOCIA_DEFAULT_ANTHROPIC_TOKEN"),
])
def test_global_default_provider_token_is_used_and_personal_token_wins(sql_chat, monkeypatch, provider_id, model_id, environment_variable):
    from app.domain.user.provider_token import ProviderToken
    from app.infrastructure.user.sqlite_repositories import TokenRepository

    client, database, _ = sql_chat
    monkeypatch.setenv(environment_variable, "server-default-token")
    monkeypatch.setattr(chat_routes, "google_quota_models", lambda key: {"gemini-test"})
    calls = []

    def generate(self, provider, model, prompt, api_key):
        calls.append(api_key)
        return "Respuesta del proveedor"

    monkeypatch.setattr(chat_routes.AIResponder, "generate", generate)
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    payload = {"prompt": "Hola", "providerId": provider_id, "modelId": model_id, "requestId": str(uuid4())}

    assert client.post(endpoint, json=payload).status_code == 200
    assert calls == ["server-default-token"]

    tokens = TokenRepository(database)
    tokens.save(ProviderToken.create(str(uuid4()), "chat@example.com", provider_id, "personal-token"))
    tokens.save_secret("chat@example.com", provider_id, "personal-token")
    payload["requestId"] = str(uuid4())

    assert client.post(endpoint, json=payload).status_code == 200
    assert calls == ["server-default-token", "personal-token"]


def test_failed_classification_can_retry_without_partial_messages(sql_chat):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    payload = {"prompt": "Explicá una idea", "requestId": str(uuid4())}
    models.fail = True
    assert client.post(f"/chat/conversations/{identifier}/messages", json=payload).status_code == 503
    assert not database.query("SELECT * FROM messages")
    models.fail = False
    assert client.post(f"/chat/conversations/{identifier}/messages", json=payload).status_code == 200
    assert len(database.query("SELECT * FROM messages")) == 2
    changed = {**payload, "prompt": "Otra consulta"}
    assert client.post(f"/chat/conversations/{identifier}/messages", json=changed).status_code == 409


def test_other_users_cannot_read_send_or_delete_and_anonymous_is_denied(sql_chat):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    client.post("/auth/logout")
    assert client.get("/chat/conversations").status_code == 401
    client.post("/auth/register", json={"mail": "other@example.com", "password": "ClaveSegura-123", "age": 22, "profession": "Docente"})
    assert client.get("/chat/conversations").json() == {"conversations": []}
    assert client.get(f"/chat/conversations/{identifier}").status_code == 404
    assert client.delete(f"/chat/conversations/{identifier}").status_code == 404
    assert client.post(f"/chat/conversations/{identifier}/messages", json={"prompt": "Hola", "requestId": str(uuid4())}).status_code == 404
    assert models.calls == 0


def test_redaction_delete_cascade_and_input_validation(sql_chat):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    assert client.post(endpoint, json={"prompt": " ", "requestId": str(uuid4())}).status_code == 422
    assert client.post(endpoint, json={"prompt": "x" * 4001, "requestId": str(uuid4())}).status_code == 422
    prompt = "Me llamo Julia. Mi correo es julia@example.com y mi teléfono es +54 11 2345 6789."
    response = client.post(endpoint, json={"prompt": prompt, "requestId": str(uuid4())})
    assert response.status_code == 200
    content = response.json()["messages"][0]["content"]
    assert "julia@example.com" not in content and "2345" not in content and "Julia" not in content
    assert "[CORREO]" in content and "[TELÉFONO]" in content and "[NOMBRE]" in content
    assert client.delete(f"/chat/conversations/{identifier}").status_code == 204
    assert not database.query("SELECT * FROM messages")
    assert not database.query("SELECT * FROM chat_turns")
    assert database.health()["ok"]


def test_chat_passes_current_profile_and_conversation_to_selected_model(sql_chat, monkeypatch):
    client, database, _ = sql_chat

    class FakeResponder:
        supported_providers = {"openai", "google", "anthropic"}

        def __init__(self):
            self.prompts = []

        def generate(self, provider_id, model_id, prompt, api_key):
            self.prompts.append(prompt)
            return f"Respuesta {len(self.prompts)}"

    responder = FakeResponder()
    client.app.dependency_overrides[chat_routes.ai_responder] = lambda: responder
    monkeypatch.setattr(chat_routes, "local_free_models", lambda: [{"providerId": "local", "modelId": "qwen3-local"}])
    assert client.patch("/profile", json={"age": 29, "profession": "Docente", "displayName": "Ana"}).status_code == 200

    first_conversation = client.post("/chat/conversations").json()["id"]
    second_conversation = client.post("/chat/conversations").json()["id"]
    payload = {"providerId": "local", "modelId": "qwen3-local"}
    client.post(f"/chat/conversations/{second_conversation}/messages", json={**payload, "prompt": "Pregunta de otro chat", "requestId": str(uuid4())})
    client.post(f"/chat/conversations/{first_conversation}/messages", json={**payload, "prompt": "¿Qué es una API?", "requestId": str(uuid4())})
    client.post(f"/chat/conversations/{first_conversation}/messages", json={**payload, "prompt": "Dame un ejemplo", "requestId": str(uuid4())})

    first, second = responder.prompts[-2:]
    assert "Nombre visible: Ana" in first
    assert "Edad: 29 años" in first
    assert "Profesión o actividad: Docente" in first
    assert "Pregunta de otro chat" not in first and "Pregunta de otro chat" not in second
    assert "¿Qué es una API?" in second
    assert "Respuesta 2" in second
    assert second.endswith("Consulta actual:\nDame un ejemplo")


def test_generation_starts_after_classification_and_progress_is_private(sql_chat, monkeypatch):
    client, database, _ = sql_chat
    repository = ChatRepository(database)
    identifier = client.post("/chat/conversations").json()["id"]
    request_id = str(uuid4())
    phases = []

    def classify(prompt):
        phases.append(repository.progress("chat@example.com", identifier, request_id)["phase"])
        return {"label": "no_personal"}

    def generate(self, *args):
        phases.append(repository.progress("chat@example.com", identifier, request_id)["phase"])
        return "Respuesta"

    monkeypatch.setattr(sql_chat[2], "classify", classify)
    monkeypatch.setattr(chat_routes.AIResponder, "generate", generate)
    monkeypatch.setattr(chat_routes, "local_free_models", lambda: [{"providerId": "local"}])
    endpoint = f"/chat/conversations/{identifier}/messages"
    assert client.post(endpoint, json={"prompt": "Consulta", "requestId": request_id, "providerId": "local", "modelId": "qwen3-local"}).status_code == 200
    assert phases == ["classifying", "generating"]
    progress_endpoint = f"{endpoint}/{request_id}/progress"
    assert client.get(progress_endpoint).json() == {"phase": "generating", "state": "completed"}
    client.post("/auth/logout")
    client.post("/auth/register", json={"mail": "other@example.com", "password": "ClaveSegura-123", "age": 22, "profession": "Docente"})
    assert client.get(progress_endpoint).status_code == 404


def test_recent_context_is_bounded_to_answered_turns_and_owned_conversation(sql_chat):
    client, database, _ = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    repository = ChatRepository(database)
    for number in range(12):
        request_id = str(uuid4())
        repository.reserve("chat@example.com", identifier, request_id, f"Pregunta {number}")
        repository.complete("chat@example.com", identifier, request_id, f"Pregunta {number}", f"Respuesta {number}", {},
                            "local" if number % 2 == 0 else None, "qwen3-local" if number % 2 == 0 else None)
    context = repository.recent_context("chat@example.com", identifier)
    assert [message["content"] for message in context if message["role"] == "user"] == ["Pregunta 4", "Pregunta 6", "Pregunta 8", "Pregunta 10"]
    assert len(context) == 8
    with pytest.raises(ConversationNotFoundError):
        repository.recent_context("other@example.com", identifier)


def test_personal_decision_does_not_call_any_answer_model(sql_chat, monkeypatch):
    client, _, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    monkeypatch.setattr(models, "classify", lambda prompt: {"label": "personal_decision"})
    monkeypatch.setattr(chat_routes, "local_free_models", lambda: [{"providerId": "local"}])

    def unexpected(*args):
        pytest.fail("A personal decision must not be sent to a response model")

    monkeypatch.setattr(chat_routes.AIResponder, "generate", unexpected)
    response = client.post(f"/chat/conversations/{identifier}/messages", json={"prompt": "¿Qué hago?", "requestId": str(uuid4()), "providerId": "local", "modelId": "qwen3-local"})
    assert response.status_code == 200
    assert not response.json().get("confirmationRequired", False)
    assert response.json()["messages"][-1]["providerId"] is None
    assert response.json()["usageLock"]["personalQuestions"] == 1


@pytest.mark.parametrize("acceptance", [{}, {"acceptPersonalResponse": False}])
def test_personal_informativa_preview_can_repeat_without_consuming_usage(sql_chat, monkeypatch, acceptance):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    previous = client.post(endpoint, json={"prompt": "Explicá una API", "requestId": str(uuid4())}).json()
    classification = {"label": "personal_informativa", "group": "personal", "confidence": 0.91, "status": "aceptada", "needs_human_review": False}
    monkeypatch.setattr(models, "classify", lambda prompt: classification)

    def unexpected(*args):
        pytest.fail("An unconfirmed personal response must not be generated")

    monkeypatch.setattr(chat_routes.AIResponder, "generate", unexpected)
    request_id = str(uuid4())
    payload = {"prompt": "Quiero información para mi caso", "requestId": request_id, **acceptance}
    event_count = len(database.query("SELECT * FROM usage_events"))

    for _ in range(2):
        response = client.post(endpoint, json=payload)
        assert response.status_code == 202
        assert response.headers["cache-control"] == "no-store"
        preview = response.json()
        assert preview["confirmationRequired"] is True
        assert preview["classification"] == classification
        assert preview["conversation"] == previous["conversation"]
        assert preview["messages"] == previous["messages"]
        assert preview["usageLock"]["blocked"] is False
        assert preview["usageLock"]["personalQuestions"] == 0
        assert preview["usageLock"]["personalQuestionsRemaining"] == 3

    turn = database.query("SELECT * FROM chat_turns WHERE request_id=?", (request_id,))[0]
    assert turn["state"] == "failed"
    assert turn["completed_at"] is None
    assert len(database.query("SELECT * FROM messages")) == 2
    assert len(database.query("SELECT * FROM usage_events")) == event_count
    dashboard = client.get("/usage/dashboard").json()
    assert dashboard["summary"]["totalQueries"] == 1
    assert dashboard["summary"]["personalQueries"] == 0
    assert client.post(endpoint, json={**payload, "prompt": "Otra consulta", "acceptPersonalResponse": True}).status_code == 409


def test_personal_informativa_generates_once_after_confirmation(sql_chat, monkeypatch):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    request_id = str(uuid4())
    repository = ChatRepository(database)
    monkeypatch.setattr(models, "classify", lambda prompt: {"label": "personal_informativa"})
    monkeypatch.setattr(chat_routes, "local_free_models", lambda: [{"providerId": "local"}])
    generated = []

    def generate(self, provider, model, prompt, api_key):
        assert repository.progress("chat@example.com", identifier, request_id)["phase"] == "generating"
        generated.append((provider, model, prompt))
        return "Respuesta personal confirmada"

    monkeypatch.setattr(chat_routes.AIResponder, "generate", generate)
    payload = {"prompt": "Quiero información para mi caso", "requestId": request_id, "providerId": "local", "modelId": "qwen3-local"}
    assert client.post(endpoint, json=payload).status_code == 202
    assert not generated
    confirmed = client.post(endpoint, json={**payload, "acceptPersonalResponse": True})
    assert confirmed.status_code == 200
    result = confirmed.json()
    assert not result.get("confirmationRequired", False)
    assert result["messages"][-1]["content"] == "Respuesta personal confirmada"
    assert result["messages"][-1]["classification"]["label"] == "personal_informativa"
    assert result["usageLock"]["personalQuestions"] == 1
    assert result["usageLock"]["personalQuestionsRemaining"] == 2
    assert len(generated) == 1

    for acceptance in [{"acceptPersonalResponse": True}, {}]:
        retry = client.post(endpoint, json={**payload, **acceptance})
        assert retry.status_code == 200
        assert retry.json() == result
    assert len(generated) == 1
    assert len(database.query("SELECT * FROM messages")) == 2
    assert len(database.query("SELECT * FROM usage_events WHERE json_extract(payload,'$.event_type')='chat_message_sent'")) == 1
    assert client.get("/usage/dashboard").json()["summary"]["personalQueries"] == 1


@pytest.mark.parametrize("acceptance", ["true", 1, None])
def test_personal_response_acceptance_requires_an_explicit_boolean(sql_chat, acceptance):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    response = client.post(
        f"/chat/conversations/{identifier}/messages",
        json={"prompt": "Consulta personal", "requestId": str(uuid4()), "acceptPersonalResponse": acceptance},
    )
    assert response.status_code == 422
    assert models.calls == 0
    assert not database.query("SELECT * FROM messages")
    assert not database.query("SELECT * FROM chat_turns")


def test_personal_informativa_predefined_response_requires_confirmation(sql_chat, monkeypatch):
    client, database, models = sql_chat
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    monkeypatch.setattr(models, "classify", lambda prompt: {"label": "personal_informativa"})

    def unexpected(*args):
        pytest.fail("A predefined response does not require a response model")

    monkeypatch.setattr(chat_routes.AIResponder, "generate", unexpected)
    payload = {"prompt": "¿Por qué me duele el tobillo?", "requestId": str(uuid4())}
    preview = client.post(endpoint, json=payload)
    assert preview.status_code == 202
    assert preview.json()["messages"] == []
    assert preview.json()["usageLock"]["personalQuestionsRemaining"] == 3
    assert not database.query("SELECT * FROM messages")
    confirmed = client.post(endpoint, json={**payload, "acceptPersonalResponse": True})
    assert confirmed.status_code == 200
    assert confirmed.json()["messages"][-1]["content"] == "No puedo evaluar síntomas ni dar un diagnóstico. Consultá con un profesional de la salud."
    assert confirmed.json()["messages"][-1]["providerId"] is None
    assert confirmed.json()["usageLock"]["personalQuestionsRemaining"] == 2


def test_pending_turn_prevents_parallel_personal_usage_in_another_conversation(sql_chat, monkeypatch):
    client, _, models = sql_chat
    first_identifier = client.post("/chat/conversations").json()["id"]
    second_identifier = client.post("/chat/conversations").json()["id"]
    classifications = []
    parallel_responses = []

    def classify(prompt):
        classifications.append(prompt)
        if len(classifications) == 1:
            parallel_responses.append(client.post(
                f"/chat/conversations/{second_identifier}/messages",
                json={"prompt": "Consulta paralela", "requestId": str(uuid4()), "acceptPersonalResponse": True},
            ))
        return {"label": "personal_informativa"}

    monkeypatch.setattr(models, "classify", classify)
    response = client.post(
        f"/chat/conversations/{first_identifier}/messages",
        json={"prompt": "Consulta inicial", "requestId": str(uuid4()), "acceptPersonalResponse": True},
    )
    assert response.status_code == 200
    assert len(classifications) == 1
    assert parallel_responses[0].status_code == 409
    assert response.json()["usageLock"]["personalQuestions"] == 1
    assert client.get(f"/chat/conversations/{second_identifier}").json()["messages"] == []


def test_three_personal_questions_lock_chat_and_dashboard_reports_reasons(sql_chat, monkeypatch):
    client, _, models = sql_chat
    labels = iter(["personal_informativa", "personal_decision", "personal_informativa"])
    monkeypatch.setattr(models, "classify", lambda prompt: {"label": next(labels), "group": "personal", "confidence": 0.91, "status": "aceptada", "needs_human_review": False})
    identifier = client.post("/chat/conversations").json()["id"]
    endpoint = f"/chat/conversations/{identifier}/messages"
    last_payload = None
    for index in range(3):
        last_payload = {"prompt": f"Consulta personal {index + 1}", "requestId": str(uuid4()), "acceptPersonalResponse": True}
        response = client.post(endpoint, json=last_payload)
        assert response.status_code == 200
        assert response.json()["usageLock"]["personalQuestionsRemaining"] == 2 - index

    status = client.get("/chat/status").json()
    assert status["usageLock"]["blocked"] is True
    assert status["usageLock"]["reasonCodes"] == ["personal_questions"]
    assert status["usageLock"]["personalQuestions"] == 3
    assert status["usageLock"]["personalQuestionsRemaining"] == 0
    assert status["usageLock"]["lockDurationMinutes"] == 1440
    assert status["usageLock"]["lockUntil"] is not None
    repeated = client.post(endpoint, json=last_payload)
    assert repeated.status_code == 200
    assert repeated.json() == response.json()
    from datetime import datetime
    from app.infrastructure.usage_analytics_repository import UsageAnalyticsRepository
    expired = UsageAnalyticsRepository(sql_chat[1]).current_lock("chat@example.com", datetime.fromisoformat(status["usageLock"]["lockUntil"]).timestamp() + 0.1)
    assert expired["blocked"] is False

    blocked = client.post(endpoint, json={"prompt": "Consulta número cuatro", "requestId": str(uuid4())})
    assert blocked.status_code == 423
    assert "3 consultas personales" in blocked.json()["detail"]["message"]
    assert "24 horas" in blocked.json()["detail"]["message"]

    dashboard = client.get("/usage/dashboard?limit=2&offset=0").json()
    assert dashboard["limits"]["blocked"] is True
    assert dashboard["summary"]["totalQueries"] == 3
    assert dashboard["summary"]["categoryCounts"]["personal_informativa"] == 2
    assert dashboard["summary"]["categoryCounts"]["personal_decision"] == 1
    assert dashboard["activity"]["total"] == 3
    assert len(dashboard["activity"]["items"]) == 2
    assert dashboard["activity"]["hasMore"] is True
    assert dashboard["activity"]["items"][0]["prompt"] == "Consulta personal 3"


def test_three_hours_of_recorded_ai_time_create_a_24_hour_lock(sql_chat):
    client, database, _ = sql_chat
    import time
    from app.infrastructure.chat_repository import ChatRepository

    identifier = client.post("/chat/conversations").json()["id"]
    repository = ChatRepository(database)
    request_id = str(uuid4())
    repository.reserve("chat@example.com", identifier, request_id, "Consulta previa")
    database.execute("UPDATE chat_turns SET started_at=? WHERE conversation_id=? AND request_id=?", (time.time() - 10801, identifier, request_id))
    repository.complete("chat@example.com", identifier, request_id, "Consulta previa", "Respuesta", {"label": "no_personal"})

    response = client.post(f"/chat/conversations/{identifier}/messages", json={"prompt": "Consulta que supera el límite", "requestId": str(uuid4())})
    assert response.status_code == 423
    assert response.json()["detail"]["message"] == "Alcanzaste el límite de 3 horas de uso de IA. La IA está bloqueada durante 24 horas."
    lock = client.get("/usage/limits").json()
    assert lock["blocked"] is True
    assert lock["reasonCodes"] == ["usage_time"]
    assert lock["usageSeconds"] >= 10800
    assert lock["lockUntil"] is not None


def test_recent_personal_history_is_enforced_even_before_a_saved_lock(sql_chat):
    client, database, _ = sql_chat
    repository = ChatRepository(database)
    identifier = client.post("/chat/conversations").json()["id"]
    for _ in range(3):
        request_id = str(uuid4())
        repository.reserve("chat@example.com", identifier, request_id, "Consulta personal")
        repository.complete("chat@example.com", identifier, request_id, "Consulta personal", "Respuesta", {"label": "personal_decision"})

    lock = client.get("/usage/limits").json()
    assert lock["blocked"] is True
    assert lock["reasonCodes"] == ["personal_questions"]
    blocked = client.post(f"/chat/conversations/{identifier}/messages", json={"prompt": "Cuarta consulta", "requestId": str(uuid4())})
    assert blocked.status_code == 423

@pytest.mark.parametrize('allowed', [set(), {'gemini-flash'}])
def test_google_rejects_unverified_or_zero_quota_model_before_processing(sql_chat, monkeypatch, allowed):
    client, database, models = sql_chat
    monkeypatch.setenv('BLOCIA_DEFAULT_GOOGLE_TOKEN', 'test-key')
    monkeypatch.setattr(chat_routes, 'google_quota_models', lambda key: allowed)
    identifier = client.post('/chat/conversations').json()['id']
    response = client.post(f'/chat/conversations/{identifier}/messages', json={'prompt': 'Consulta', 'requestId': str(uuid4()), 'providerId': 'google', 'modelId': 'gemini-pro'})
    assert response.status_code == 422
    assert models.calls == 0
    assert not database.query('SELECT * FROM messages')
