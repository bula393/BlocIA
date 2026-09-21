from app.presentation.user import auth_routes


def test_google_start_without_configuration_returns_to_front(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    response = client.get("/auth/google/start", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"].endswith("/auth/google/callback?error=configuration")


def test_google_callback_uses_one_time_session_result(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(auth_routes, "google_identity", lambda code: {
        "sub": "google-subject",
        "email": "new.google@example.com",
        "email_verified": True,
        "aud": "test-client",
    })
    client.cookies.set("bloqia_google_state", "verified-state")

    callback = client.get("/auth/google/callback?code=provider-code&state=verified-state", follow_redirects=False)
    session = client.get("/auth/google/session")
    consumed = client.get("/auth/google/session")

    assert callback.status_code == 302
    assert session.status_code == 200
    assert session.json()["prefilledFields"]["mail"] == "new.google@example.com"
    assert session.json()["missingFields"] == ["age", "profession"]
    assert consumed.status_code == 401
