from app.domain.user.enums import ProviderTokenStatusValue
from app.domain.user.repositories import AIModelRepository, AIProviderRepository, ProviderTokenRepository


class ListTechnicalProviders:
    def __init__(self, providers: AIProviderRepository, models: AIModelRepository, tokens: ProviderTokenRepository):
        self.providers = providers
        self.models = models
        self.tokens = tokens

    def execute(self, user_mail: str) -> list[dict]:
        result: list[dict] = []
        for provider in self.providers.list():
            token = self.tokens.get(user_mail, provider.provider_id)
            token_status = token.status if token else ProviderTokenStatusValue.NOT_CONFIGURED
            result.append({
                "provider": provider,
                "models": self.models.list_by_provider(provider.provider_id),
                "token": token,
                "token_status": token_status,
            })
        return result
