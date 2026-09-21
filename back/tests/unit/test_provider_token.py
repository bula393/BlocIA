from app.domain.user.provider_token import ProviderToken


def test_provider_token_masks_secret_and_tracks_owner():
    token = ProviderToken.create("1", "user@example.com", "openai", "secret-token-value")
    assert token.user_mail == "user@example.com"
    assert token.provider_id == "openai"
    assert "secret-token-value" not in token.masked_token_label
    assert token.status == "configured"
