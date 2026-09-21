def test_profile_contract(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    assert client.get("/profile", headers=headers).status_code == 200
    assert client.get("/profile").status_code == 401
    assert client.patch("/profile", headers=headers, json={"profession": "Analista"}).status_code == 200
