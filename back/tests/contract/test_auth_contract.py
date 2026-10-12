def test_auth_contract(client, seeded_user):
    assert client.post("/auth/login", json={"mail": seeded_user.mail, "password": "ClaveSegura-123"}).status_code == 200
    assert client.post("/auth/login", json={"mail": seeded_user.mail, "password": "incorrecta"}).status_code == 401
    assert client.get("/auth/google/start", follow_redirects=False).status_code == 302
    assert client.get("/auth/google/session").status_code == 401


def test_browser_session_is_restored_until_logout(client, seeded_user):
    login = client.post("/auth/login", json={"mail": seeded_user.mail, "password": "ClaveSegura-123"})

    assert login.status_code == 200
    assert "bloqia_session=" in login.headers["set-cookie"]
    assert "Max-Age" not in login.headers["set-cookie"]
    assert client.get("/auth/session").status_code == 200
    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/session").status_code == 401
    assert client.get("/profile", headers={"Authorization": f"Bearer {login.json()['accessToken']}"}).status_code == 401


def test_cookie_authenticated_mutation_rejects_sibling_origin(client, seeded_user):
    login = client.post("/auth/login", json={"mail": seeded_user.mail, "password": "ClaveSegura-123"})
    assert login.status_code == 200

    rejected = client.patch(
        "/profile", json={"displayName": "Atacante"}, headers={"Origin": "https://sibling.example.com"}
    )
    accepted = client.patch(
        "/profile", json={"displayName": "Usuario"},
        headers={"Origin": client.app.state.runtime_settings.frontend_url},
    )

    assert rejected.status_code == 403
    assert accepted.status_code == 200


def test_production_cookie_mutation_requires_origin(monkeypatch, seeded_user):
    from fastapi.testclient import TestClient
    from app.infrastructure.user.postgres_repositories import UserRepositoryImpl, PasswordCredentialRepositoryImpl
    from app.presentation.user import dependencies
    from app.main import create_app

    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("FRONTEND_URL", "https://blocia.example.com")
    monkeypatch.setenv("ACCESS_TOKEN_SECRET", "test-production-access-token-secret-000000000000")
    monkeypatch.setenv("BLOCIA_PRELOAD_CLASSIFIER", "0")
    monkeypatch.setenv("BLOCIA_PRELOAD_LOCAL_CHAT", "0")
    app = create_app()
    app.dependency_overrides[dependencies.user_repo] = lambda: UserRepositoryImpl()
    app.dependency_overrides[dependencies.credential_repo] = lambda: PasswordCredentialRepositoryImpl()

    with TestClient(app, base_url="https://blocia.example.com") as production_client:
        login = production_client.post("/auth/login", json={"mail": seeded_user.mail, "password": "ClaveSegura-123"})
        assert login.status_code == 200
        denied = production_client.patch("/profile", json={"displayName": "Sin origen"})

    assert denied.status_code == 403
