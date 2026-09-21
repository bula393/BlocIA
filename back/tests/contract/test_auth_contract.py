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
