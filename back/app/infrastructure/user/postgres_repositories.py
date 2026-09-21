from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.user.ai_model import AIModel
from app.domain.user.ai_provider import AIProvider
from app.domain.user.enums import ModelAvailabilityStatus, ProviderStatus
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.password_credential import PasswordCredential
from app.domain.user.provider_token import ProviderToken
from app.domain.user.user import User


@dataclass
class InMemoryUserStore:
    users: dict[str, User] = field(default_factory=dict)
    credentials: dict[str, PasswordCredential] = field(default_factory=dict)
    external_links: dict[tuple[str, str], ExternalLoginLink] = field(default_factory=dict)
    providers: dict[str, AIProvider] = field(default_factory=dict)
    models: dict[str, list[AIModel]] = field(default_factory=dict)
    tokens: dict[tuple[str, str], ProviderToken] = field(default_factory=dict)

    def seed_defaults(self) -> None:
        if not self.providers:
            self.providers["openai"] = AIProvider("openai", "OpenAI", ProviderStatus.AVAILABLE, "OpenAI models")
            self.providers["google"] = AIProvider("google", "Google AI", ProviderStatus.AVAILABLE, "Google AI models")
            self.models["openai"] = [AIModel("gpt-4o-mini", "openai", "GPT-4o mini", ModelAvailabilityStatus.AVAILABLE, ["chat"])]
            self.models["google"] = [AIModel("gemini-1.5-flash", "google", "Gemini 1.5 Flash", ModelAvailabilityStatus.AVAILABLE, ["chat"])]


STORE = InMemoryUserStore()
STORE.seed_defaults()


class UserRepositoryImpl:
    def __init__(self, store: InMemoryUserStore = STORE):
        self.store = store

    def get(self, mail: str) -> User | None:
        return self.store.users.get(mail)

    def save(self, user: User) -> User:
        user.validate()
        self.store.users[user.mail] = user
        return user

    def exists(self, mail: str) -> bool:
        return mail in self.store.users


class PasswordCredentialRepositoryImpl:
    def __init__(self, store: InMemoryUserStore = STORE):
        self.store = store

    def get(self, user_mail: str) -> PasswordCredential | None:
        return self.store.credentials.get(user_mail)

    def save(self, credential: PasswordCredential) -> PasswordCredential:
        self.store.credentials[credential.user_mail] = credential
        return credential


class ExternalLoginLinkRepositoryImpl:
    def __init__(self, store: InMemoryUserStore = STORE):
        self.store = store

    def get_by_subject(self, provider: str, external_subject: str) -> ExternalLoginLink | None:
        return self.store.external_links.get((provider, external_subject))

    def save(self, link: ExternalLoginLink) -> ExternalLoginLink:
        self.store.external_links[(link.provider, link.external_subject)] = link
        return link


class AIProviderRepositoryImpl:
    def __init__(self, store: InMemoryUserStore = STORE):
        self.store = store

    def list(self) -> list[AIProvider]:
        return list(self.store.providers.values())

    def get(self, provider_id: str) -> AIProvider | None:
        return self.store.providers.get(provider_id)


class AIModelRepositoryImpl:
    def __init__(self, store: InMemoryUserStore = STORE):
        self.store = store

    def list_by_provider(self, provider_id: str) -> list[AIModel]:
        return self.store.models.get(provider_id, [])


class ProviderTokenRepositoryImpl:
    def __init__(self, store: InMemoryUserStore = STORE):
        self.store = store

    def get(self, user_mail: str, provider_id: str) -> ProviderToken | None:
        return self.store.tokens.get((user_mail, provider_id))

    def save(self, token: ProviderToken) -> ProviderToken:
        self.store.tokens[(token.user_mail, token.provider_id)] = token
        return token

    def delete(self, user_mail: str, provider_id: str) -> bool:
        return self.store.tokens.pop((user_mail, provider_id), None) is not None

    def list_for_user(self, user_mail: str) -> list[ProviderToken]:
        return [token for (mail, _), token in self.store.tokens.items() if mail == user_mail]
