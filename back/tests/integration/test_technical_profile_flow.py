def test_technical_profile_provider_token_lifecycle(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    providers = client.get("/technical-profile/providers", headers=headers)
    assert providers.status_code == 200
    assert providers.json()["providers"]

    saved = client.post("/technical-profile/tokens", headers=headers, json={"providerId": "openai", "token": "test-token-value"})
    assert saved.status_code == 200
    assert saved.json()["status"] == "configured"
    assert "test-token-value" not in str(saved.json())

    replaced = client.post("/technical-profile/tokens", headers=headers, json={"providerId": "openai", "token": "other-token-value"})
    assert replaced.status_code == 200

    removed = client.delete("/technical-profile/tokens/openai", headers=headers)
    assert removed.status_code == 204
