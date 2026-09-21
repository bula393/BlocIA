def test_technical_profile_contract(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    assert client.get("/technical-profile/providers", headers=headers).status_code == 200
    assert client.post("/technical-profile/tokens", headers=headers, json={"providerId": "openai", "token": "abc123"}).status_code == 200
    assert client.delete("/technical-profile/tokens/openai", headers=headers).status_code == 204
