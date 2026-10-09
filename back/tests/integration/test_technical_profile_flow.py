from app.application.user import list_available_models
from app.domain.user.ai_model import AIModel
from app.domain.user.enums import ModelAvailabilityStatus


def test_technical_profile_provider_token_lifecycle(client, access_token, verified_email):
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


def test_usage_summary_uses_saved_events_and_tokens(client, access_token, verified_email):
    headers = {"Authorization": f"Bearer {access_token}"}
    client.post("/technical-profile/tokens", headers=headers, json={"providerId": "anthropic", "token": "test-token"})
    client.get("/technical-profile/providers/openai/models", headers=headers)

    response = client.get("/usage/today", headers=headers)

    assert response.status_code == 200
    assert response.json()["configuredProviders"] == 1
    assert response.json()["modelCatalogRequests"] == 1
    assert response.json()["lastActivityAt"] is not None


def test_default_provider_token_is_available_without_exposing_its_value(client, access_token, monkeypatch):
    monkeypatch.setenv("BLOCIA_DEFAULT_OPENAI_TOKEN", "server-only-test-token")
    monkeypatch.setattr(
        list_available_models.OpenAIModelsClient,
        "list_models",
        lambda self, api_key: [AIModel("gpt-test", "openai", "GPT test", ModelAvailabilityStatus.AVAILABLE, ["texto"])],
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    providers = client.get("/technical-profile/providers", headers=headers)
    openai = next(row for row in providers.json()["providers"] if row["providerId"] == "openai")
    models = client.get("/technical-profile/providers/openai/models", headers=headers)

    assert openai["defaultTokenAvailable"] is True
    assert openai["tokenStatus"]["status"] == "not-configured"
    assert "server-only-test-token" not in providers.text
    assert models.json()["source"] == "default"
    assert models.json()["models"][0]["modelId"] == "gpt-test"
    assert "server-only-test-token" not in models.text


def test_google_catalog_only_offers_project_quota_models(client, access_token, monkeypatch, tmp_path, verified_email):
    import hashlib
    import json
    path = tmp_path / "quotas.json"
    path.write_text(json.dumps({"credentialSha256": hashlib.sha256(b"test-key").hexdigest(), "projectId": "test", "checkedAt": "2026-10-06", "models": [{"modelId": "flash", "chat": True, "rpm": 5, "tpm": 250000, "rpd": 20}]}))
    monkeypatch.setenv("BLOCIA_GOOGLE_MODEL_ACCESS_PATH", str(path))
    monkeypatch.setenv("BLOCIA_DEFAULT_GOOGLE_TOKEN", "test-key")
    monkeypatch.setattr(list_available_models.GoogleModelsClient, "list_models", lambda self, key: [
        AIModel("flash", "google", "Flash"), AIModel("pro", "google", "Pro"), AIModel("audio", "google", "Audio"),
    ])
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/technical-profile/providers/google/models", headers=headers)
    assert response.status_code == 200
    assert [row["modelId"] for row in response.json()["models"]] == ["flash"]
    assert "test-key" not in response.text
    client.post("/technical-profile/tokens", headers=headers, json={"providerId": "google", "token": "different-project-key"})
    response = client.get("/technical-profile/providers/google/models", headers=headers)
    assert response.status_code != 200
    assert "No se verificó la cuota" in response.text
