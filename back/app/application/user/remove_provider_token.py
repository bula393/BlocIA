from app.domain.user.repositories import ProviderTokenRepository


class RemoveProviderToken:
    def __init__(self, tokens: ProviderTokenRepository):
        self.tokens = tokens

    def execute(self, user_mail: str, provider_id: str) -> bool:
        return self.tokens.delete(user_mail, provider_id)
