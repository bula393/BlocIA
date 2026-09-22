from uuid import uuid4
from contextlib import nullcontext

from app.domain.user.provider_token import ProviderToken
from app.domain.user.repositories import AIProviderRepository, ProviderTokenRepository


class ProviderUnavailableError(Exception):
    pass


class SaveProviderToken:
    def __init__(self, providers: AIProviderRepository, tokens: ProviderTokenRepository):
        self.providers = providers
        self.tokens = tokens

    def execute(self, user_mail: str, provider_id: str, raw_token: str) -> ProviderToken:
        with getattr(self.tokens, "transaction", nullcontext)():
            return self._execute(user_mail, provider_id, raw_token)

    def _execute(self, user_mail: str, provider_id: str, raw_token: str) -> ProviderToken:
        provider = self.providers.get(provider_id)
        if provider is None or not provider.can_accept_token():
            raise ProviderUnavailableError("Invalid provider or token data")
        existing = self.tokens.get(user_mail, provider_id)
        if existing:
            existing.replace(raw_token)
            token = self.tokens.save(existing)
        else:
            token = self.tokens.save(ProviderToken.create(str(uuid4()), user_mail, provider_id, raw_token))
        self.tokens.save_secret(user_mail, provider_id, raw_token)
        return token
