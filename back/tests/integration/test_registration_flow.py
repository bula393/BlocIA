from app.application.user.google_auth import registration_token


def test_registration_duplicate_weak_and_google_completion(client):
    payload = {"mail": "nuevo.usuario@example.com", "password": "ClaveSegura-123", "age": 28, "profession": "Estudiante"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json={**payload, "password": "OtraClave-123"}).status_code == 409
    assert client.post("/auth/register", json={"mail": "weak@example.com", "password": "123", "age": 20, "profession": "Estudiante"}).status_code == 422
    token = registration_token("google-subject", "google.user@example.com")
    assert client.post("/auth/register/complete-google", json={"registrationToken": token, "age": 20, "profession": "Docente"}).status_code == 201
    assert client.post("/auth/register/complete-google", json={"registrationToken": "google-subject", "age": 20, "profession": "Docente"}).status_code == 400
