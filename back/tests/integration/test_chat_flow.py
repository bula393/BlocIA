from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from app.application.chat.local_models import local_models, ModelUnavailableError
from app.infrastructure.database import Database, get_database
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
def sql_chat(tmp_path):
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
    assert first.json()["messages"][1]["classification"]["label"] == "no_personal"
    assert client.post(endpoint, json=payload).json() == first.json()
    assert models.calls == 1
    follow_up = client.post(endpoint, json={"prompt": "Dame un ejemplo", "requestId": str(uuid4())})
    assert follow_up.json()["messages"][-1]["classification"]["label"] == "no_personal"
    assert len(Database(database.path).query("SELECT * FROM messages")) == 4
    assert client.get(f"/chat/conversations/{identifier}").json()["messages"] == follow_up.json()["messages"]
    assert client.get("/health").json()["database"]["ok"]


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
