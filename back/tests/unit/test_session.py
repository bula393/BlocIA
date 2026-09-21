from app.application.user.session import create_access_token, parse_access_token


def test_access_token_is_signed_and_expires(monkeypatch):
    monkeypatch.setenv("ACCESS_TOKEN_SECRET", "test-session-secret")
    token = create_access_token("usuario@example.com")

    assert token.count(".") == 2
    assert parse_access_token(token) == "usuario@example.com"
    assert parse_access_token(f"{token}x") is None
    assert parse_access_token(create_access_token("usuario@example.com", expires_in_seconds=0)) is None
