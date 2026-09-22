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


def test_openai_models_without_token_returns_free_open_weight_options(client, access_token):
    response = client.get("/technical-profile/providers/openai/models", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert response.json()["source"] == "free"
    assert {model["modelId"] for model in response.json()["models"]} == {"gpt-oss-20b", "gpt-oss-120b"}


def test_usage_summary_uses_saved_events_and_tokens(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post("/technical-profile/tokens", headers=headers, json={"providerId": "anthropic", "token": "test-token"})
    client.get("/technical-profile/providers/openai/models", headers=headers)

    response = client.get("/usage/today", headers=headers)

    assert response.status_code == 200
    assert response.json()["configuredProviders"] == 1
    assert response.json()["modelCatalogRequests"] == 1
    assert response.json()["lastActivityAt"] is not None
