def test_profile_read_update_and_invalid_value(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/profile", headers=headers)
    assert response.status_code == 200
    assert response.json()["mail"] == "usuario.demo@example.com"

    updated = client.patch("/profile", headers=headers, json={"age": 29, "profession": "Programador"})
    assert updated.status_code == 200
    assert updated.json()["age"] == 29

    invalid = client.patch("/profile", headers=headers, json={"age": 0})
    assert invalid.status_code == 422
