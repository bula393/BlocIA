from urllib.parse import parse_qs, urlsplit

import pytest

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
    monkeypatch.setattr(auth_routes, "google_identity", lambda code, nonce: {
        "sub": "google-subject",
        "email": "new.google@example.com",
        "email_verified": True,
        "aud": "test-client",
    })
    start = client.get("/auth/google/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]

    callback = client.get("/auth/google/callback", params={"code": "provider-code", "state": state}, follow_redirects=False)
    session = client.get("/auth/google/session")
    consumed = client.get("/auth/google/session")

    assert callback.status_code == 302
    assert session.status_code == 200
    assert session.json()["prefilledFields"]["mail"] == "new.google@example.com"
    assert session.json()["missingFields"] == ["age", "profession"]
    assert consumed.status_code == 401


@pytest.mark.parametrize("state", [None, "", "wrong-state", "estado-inválido"])
def test_google_callback_rejects_invalid_state_before_contacting_google(client, monkeypatch, state):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(auth_routes, "google_identity", lambda *args: pytest.fail("Invalid state contacted Google"))
    client.get("/auth/google/start", follow_redirects=False)
    params = {"code": "provider-code"}
    if state is not None:
        params["state"] = state

    callback = client.get("/auth/google/callback", params=params, follow_redirects=False)

    assert callback.headers["location"].endswith("?error=state")
    assert "bloqia_google_state" not in client.cookies
    assert "bloqia_google_result" not in client.cookies


def test_google_transaction_expiration_is_checked_on_server(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setattr(auth_routes, "google_identity", lambda *args: pytest.fail("Expired state contacted Google"))
    monkeypatch.setattr(auth_routes.time, "time", lambda: 1000)
    start = client.get("/auth/google/start", follow_redirects=False)
    state = parse_qs(urlsplit(start.headers["location"]).query)["state"][0]
    monkeypatch.setattr(auth_routes.time, "time", lambda: 1600)

    callback = client.get("/auth/google/callback", params={"code": "provider-code", "state": state}, follow_redirects=False)

    assert callback.headers["location"].endswith("?error=state")


def test_google_start_binds_identity_nonce_and_clears_previous_result(client, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    client.cookies.set("bloqia_google_result", "old-result", domain="testserver.local", path="/")
    start = client.get("/auth/google/start", follow_redirects=False)
    params = parse_qs(urlsplit(start.headers["location"]).query)
    seen = []

    def identity(code, nonce):
        seen.append((code, nonce))
        return {"sub": "google-subject", "email": "new.google@example.com"}

    monkeypatch.setattr(auth_routes, "google_identity", identity)
    assert params["nonce"][0] != params["state"][0]
    assert "bloqia_google_result" not in client.cookies
    client.get("/auth/google/callback", params={"code": "provider-code", "state": params["state"][0]}, follow_redirects=False)

    assert seen == [("provider-code", params["nonce"][0])]


def test_google_result_expiration_is_checked_on_server(client, monkeypatch):
    monkeypatch.setattr(auth_routes.time, "time", lambda: 1000)
    result = auth_routes.encode_result({"accessToken": "test-token"})
    client.cookies.set("bloqia_google_result", result)
    monkeypatch.setattr(auth_routes.time, "time", lambda: 1120)

    assert client.get("/auth/google/session").status_code == 401


def test_google_result_cannot_be_used_as_transaction_cookie(client, monkeypatch):
    monkeypatch.setattr(auth_routes, "google_identity", lambda *args: pytest.fail("Wrong purpose contacted Google"))
    client.cookies.set("bloqia_google_state", auth_routes.encode_result({"state": "state", "nonce": "nonce"}))

    callback = client.get("/auth/google/callback?code=code&state=state", follow_redirects=False)

    assert callback.headers["location"].endswith("?error=state")
