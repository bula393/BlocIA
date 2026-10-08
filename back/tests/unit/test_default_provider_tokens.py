import pytest

from app.application.chat.default_provider_tokens import DEFAULT_TOKEN_ENV, default_provider_token


@pytest.mark.parametrize("provider_id", ["google", "groq", "openrouter", "openai", "anthropic"])
def test_default_provider_token_reads_each_provider_variable(provider_id, monkeypatch):
    variable = DEFAULT_TOKEN_ENV[provider_id]
    monkeypatch.setenv(variable, " server-default-token ")

    assert default_provider_token(provider_id) == "server-default-token"


def test_unknown_or_unconfigured_provider_has_no_default_token(monkeypatch):
    assert default_provider_token("local") is None
    monkeypatch.delenv("BLOCIA_DEFAULT_GROQ_TOKEN", raising=False)
    assert default_provider_token("groq") is None
