from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path
import sys

from app.domain.user.ai_model import AIModel
from app.domain.user.ai_provider import AIProvider
from app.domain.user.enums import LoginProviderStatus, ModelAvailabilityStatus, ProviderStatus, ProviderTokenStatusValue, TechnicalProfileStatus
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.password_credential import PasswordCredential
from app.domain.user.provider_token import ProviderToken
from app.domain.user.user import User
from app.domain.user.usage_event import UsageEvent


@dataclass
class InMemoryUserStore:
    users: dict[str, User] = field(default_factory=dict)
    credentials: dict[str, PasswordCredential] = field(default_factory=dict)
    external_links: dict[tuple[str, str], ExternalLoginLink] = field(default_factory=dict)
    providers: dict[str, AIProvider] = field(default_factory=dict)
    models: dict[str, list[AIModel]] = field(default_factory=dict)
    tokens: dict[tuple[str, str], ProviderToken] = field(default_factory=dict)
    token_secrets: dict[tuple[str, str], str] = field(default_factory=dict)
    usage_events: list[UsageEvent] = field(default_factory=list)

    def seed_defaults(self) -> None:
        self.providers.setdefault("openai", AIProvider("openai", "OpenAI", ProviderStatus.AVAILABLE, "OpenAI models"))
        self.providers.setdefault("google", AIProvider("google", "Google AI", ProviderStatus.AVAILABLE, "Google AI models"))
        self.providers.setdefault("anthropic", AIProvider("anthropic", "Claude · Anthropic", ProviderStatus.AVAILABLE, "Modelos Claude de Anthropic"))
        self.models.setdefault("openai", [AIModel("gpt-4o-mini", "openai", "GPT-4o mini", ModelAvailabilityStatus.AVAILABLE, ["chat"])])
        self.models.setdefault("google", [AIModel("gemini-1.5-flash", "google", "Gemini 1.5 Flash", ModelAvailabilityStatus.AVAILABLE, ["chat"])])
        self.models.setdefault("anthropic", [
            AIModel("claude-opus-5", "anthropic", "Claude Opus", ModelAvailabilityStatus.AVAILABLE, ["razonamiento complejo", "vision", "contexto amplio"]),
            AIModel("claude-sonnet-5", "anthropic", "Claude Sonnet", ModelAvailabilityStatus.AVAILABLE, ["trabajo diario", "vision", "codigo"]),
            AIModel("claude-haiku-4-5-20251001", "anthropic", "Claude Haiku", ModelAvailabilityStatus.AVAILABLE, ["rapido", "bajo consumo", "chat"]),
        ])


class PersistentUserStore(InMemoryUserStore):
    """Durable local store used by the app; tests retain their isolated memory store."""

    def __init__(self, path: Path, read_only: bool = False):
        super().__init__()
        self.path = path
        if path.exists():
            self._load()
        self.seed_defaults()
        if not read_only:
            self.flush()

    @staticmethod
    def _datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _load(self) -> None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            self.users = {
                mail: User(mail=mail, age=data["age"], profession=data["profession"], password_status=data["passwordStatus"], display_name=data.get("displayName"), login_provider_status=LoginProviderStatus(data["loginProviderStatus"]), technical_profile_status=TechnicalProfileStatus(data["technicalProfileStatus"]), created_at=self._datetime(data["createdAt"]) or User(mail=mail, age=1, profession="_").created_at, updated_at=self._datetime(data["updatedAt"]) or User(mail=mail, age=1, profession="_").updated_at)
                for mail, data in payload.get("users", {}).items()
            }
            self.credentials = {mail: PasswordCredential(mail, data["passwordHash"], self._datetime(data["createdAt"]) or datetime.now(), self._datetime(data["updatedAt"]) or datetime.now()) for mail, data in payload.get("credentials", {}).items()}
            self.external_links = {(data["provider"], data["externalSubject"]): ExternalLoginLink(data["userMail"], data["provider"], data["externalSubject"], data["providedMail"], data.get("providedDisplayName"), self._datetime(data["createdAt"]) or datetime.now(), self._datetime(data.get("lastUsedAt"))) for data in payload.get("externalLinks", [])}
            self.providers = {provider_id: AIProvider(provider_id, data["name"], ProviderStatus(data["status"]), data.get("description")) for provider_id, data in payload.get("providers", {}).items()}
            self.models = {provider_id: [AIModel(model["modelId"], provider_id, model["displayName"], ModelAvailabilityStatus(model["availabilityStatus"]), model.get("capabilities", [])) for model in models] for provider_id, models in payload.get("models", {}).items()}
            self.tokens = {(data["userMail"], data["providerId"]): ProviderToken(data["tokenId"], data["userMail"], data["providerId"], data["maskedTokenLabel"], ProviderTokenStatusValue(data["status"]), self._datetime(data["createdAt"]) or datetime.now(), self._datetime(data["updatedAt"]) or datetime.now(), self._datetime(data.get("lastValidatedAt"))) for data in payload.get("tokens", [])}
            self.usage_events = [UsageEvent(data["userMail"], data["eventType"], data.get("providerId"), self._datetime(data["occurredAt"]) or datetime.now()) for data in payload.get("usageEvents", [])]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"No se pudo leer la base local {self.path}. No se sobrescribió ningún dato.") from exc

    def flush(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "users": {mail: {"age": user.age, "profession": user.profession, "passwordStatus": user.password_status, "displayName": user.display_name, "loginProviderStatus": user.login_provider_status.value, "technicalProfileStatus": user.technical_profile_status.value, "createdAt": user.created_at.isoformat(), "updatedAt": user.updated_at.isoformat()} for mail, user in self.users.items()},
            "credentials": {mail: {"passwordHash": credential.password_hash, "createdAt": credential.created_at.isoformat(), "updatedAt": credential.updated_at.isoformat()} for mail, credential in self.credentials.items()},
            "externalLinks": [{"userMail": link.user_mail, "provider": link.provider, "externalSubject": link.external_subject, "providedMail": link.provided_mail, "providedDisplayName": link.provided_display_name, "createdAt": link.created_at.isoformat(), "lastUsedAt": link.last_used_at.isoformat() if link.last_used_at else None} for link in self.external_links.values()],
            "providers": {provider_id: {"name": provider.name, "status": provider.status.value, "description": provider.description} for provider_id, provider in self.providers.items()},
            "models": {provider_id: [{"modelId": model.model_id, "displayName": model.display_name, "availabilityStatus": model.availability_status.value, "capabilities": model.capabilities} for model in models] for provider_id, models in self.models.items()},
            "tokens": [{"tokenId": token.token_id, "userMail": token.user_mail, "providerId": token.provider_id, "maskedTokenLabel": token.masked_token_label, "status": token.status.value, "createdAt": token.created_at.isoformat(), "updatedAt": token.updated_at.isoformat(), "lastValidatedAt": token.last_validated_at.isoformat() if token.last_validated_at else None} for token in self.tokens.values()],
            "usageEvents": [{"userMail": event.user_mail, "eventType": event.event_type, "providerId": event.provider_id, "occurredAt": event.occurred_at.isoformat()} for event in self.usage_events],
        }
        temporary_path = self.path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        temporary_path.replace(self.path)


STORE = InMemoryUserStore()
STORE.seed_defaults()
APPLICATION_STORE = None


def default_store() -> InMemoryUserStore:
    global APPLICATION_STORE
    if "pytest" in sys.modules:
        return STORE
    if APPLICATION_STORE is None:
        APPLICATION_STORE = PersistentUserStore(Path(os.getenv("BLOCIA_DATA_PATH", str(Path(__file__).resolve().parents[3] / "data" / "blocia-state.json"))))
    return APPLICATION_STORE


def flush(store: InMemoryUserStore) -> None:
    if isinstance(store, PersistentUserStore):
        store.flush()


class UserRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def get(self, mail: str) -> User | None:
        return self.store.users.get(mail)

    def save(self, user: User) -> User:
        user.validate()
        self.store.users[user.mail] = user
        flush(self.store)
        return user

    def exists(self, mail: str) -> bool:
        return mail in self.store.users


class PasswordCredentialRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def get(self, user_mail: str) -> PasswordCredential | None:
        return self.store.credentials.get(user_mail)

    def save(self, credential: PasswordCredential) -> PasswordCredential:
        self.store.credentials[credential.user_mail] = credential
        flush(self.store)
        return credential


class ExternalLoginLinkRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def get_by_subject(self, provider: str, external_subject: str) -> ExternalLoginLink | None:
        return self.store.external_links.get((provider, external_subject))

    def save(self, link: ExternalLoginLink) -> ExternalLoginLink:
        self.store.external_links[(link.provider, link.external_subject)] = link
        flush(self.store)
        return link


class AIProviderRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def list(self) -> list[AIProvider]:
        return list(self.store.providers.values())

    def get(self, provider_id: str) -> AIProvider | None:
        return self.store.providers.get(provider_id)


class AIModelRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def list_by_provider(self, provider_id: str) -> list[AIModel]:
        return self.store.models.get(provider_id, [])


class ProviderTokenRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def get(self, user_mail: str, provider_id: str) -> ProviderToken | None:
        return self.store.tokens.get((user_mail, provider_id))

    def save(self, token: ProviderToken) -> ProviderToken:
        self.store.tokens[(token.user_mail, token.provider_id)] = token
        flush(self.store)
        return token

    def save_secret(self, user_mail: str, provider_id: str, raw_token: str) -> None:
        """Keep the secret server-side only; public token records remain masked."""
        self.store.token_secrets[(user_mail, provider_id)] = raw_token

    def get_secret(self, user_mail: str, provider_id: str) -> str | None:
        return self.store.token_secrets.get((user_mail, provider_id))

    def delete(self, user_mail: str, provider_id: str) -> bool:
        self.store.token_secrets.pop((user_mail, provider_id), None)
        removed = self.store.tokens.pop((user_mail, provider_id), None) is not None
        flush(self.store)
        return removed

    def list_for_user(self, user_mail: str) -> list[ProviderToken]:
        return [token for (mail, _), token in self.store.tokens.items() if mail == user_mail]


class UsageEventRepositoryImpl:
    def __init__(self, store: InMemoryUserStore | None = None):
        self.store = store or default_store()

    def record(self, event: UsageEvent) -> UsageEvent:
        self.store.usage_events.append(event)
        flush(self.store)
        return event

    def list_for_user(self, user_mail: str) -> list[UsageEvent]:
        return [event for event in self.store.usage_events if event.user_mail == user_mail]
