"""Server-owned provider keys configured in the backend's development env."""

import os


DEFAULT_TOKEN_ENV = {
    "google": "BLOCIA_DEFAULT_GOOGLE_TOKEN",
    "groq": "BLOCIA_DEFAULT_GROQ_TOKEN",
    "openrouter": "BLOCIA_DEFAULT_OPENROUTER_TOKEN",
    "openai": "BLOCIA_DEFAULT_OPENAI_TOKEN",
    "anthropic": "BLOCIA_DEFAULT_ANTHROPIC_TOKEN",
}


def default_provider_token(provider_id: str) -> str | None:
    variable = DEFAULT_TOKEN_ENV.get(provider_id)
    if not variable:
        return None
    return os.getenv(variable, "").strip() or None
