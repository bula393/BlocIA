import pytest

from app.domain.user.ai_provider import AIProvider
from app.domain.user.enums import ProviderStatus


def test_provider_visibility_and_token_availability():
    provider = AIProvider("openai", "OpenAI", ProviderStatus.AVAILABLE)
    provider.validate()
    assert provider.can_accept_token()
    unavailable = AIProvider("old", "Old", ProviderStatus.UNAVAILABLE)
    assert not unavailable.can_accept_token()
    with pytest.raises(ValueError):
        AIProvider("bad", "").validate()
