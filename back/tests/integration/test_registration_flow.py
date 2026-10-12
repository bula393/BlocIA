from app.application.user.google_auth import registration_token


def test_registration_duplicate_weak_and_google_completion(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_REGISTRATION_SECRET", "test-google-registration-secret-0123456789")
    payload = {"mail": "nuevo.usuario@example.com", "password": "ClaveSegura-123", "age": 28, "profession": "Estudiante"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json={**payload, "password": "OtraClave-123"}).status_code == 409
    assert client.post("/auth/register", json={"mail": "weak@example.com", "password": "123", "age": 20, "profession": "Estudiante"}).status_code == 422
    token = registration_token("google-subject", "google.user@example.com")
    assert client.post("/auth/register/complete-google", json={"registrationToken": token, "age": 20, "profession": "Docente"}).status_code == 201
    assert client.post("/auth/register/complete-google", json={"registrationToken": "google-subject", "age": 20, "profession": "Docente"}).status_code == 400


def test_registration_daily_cap_is_shared_and_returns_retry_after(client, monkeypatch):
    from app.infrastructure.user.postgres_repositories import STORE

    monkeypatch.setenv("BLOCIA_REGISTRATION_MAX_PER_DAY", "1")
    first = {"mail": "one@example.com", "password": "ClaveSegura-123", "age": 22, "profession": "Estudiante"}
    second = {**first, "mail": "two@example.com"}

    accepted = client.post("/auth/register", json=first)
    limited = client.post("/auth/register", json=second)

    assert accepted.status_code == 201
    assert limited.status_code == 429
    assert int(limited.headers["Retry-After"]) > 0
    assert second["mail"] not in STORE.users
