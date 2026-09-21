from dataclasses import dataclass, field
from datetime import datetime, timezone

from .enums import ProviderTokenStatusValue


def _now() -> datetime:
    return datetime.now(timezone.utc)


def mask_token(token: str) -> str:
    if len(token) <= 6:
        return "***"
    return f"{token[:3]}***{token[-3:]}"


@dataclass
class ProviderToken:
    token_id: str
    user_mail: str
    provider_id: str
    masked_token_label: str
    status: ProviderTokenStatusValue = ProviderTokenStatusValue.CONFIGURED
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
    last_validated_at: datetime | None = None

    @classmethod
    def create(cls, token_id: str, user_mail: str, provider_id: str, raw_token: str) -> "ProviderToken":
        if not raw_token.strip():
            raise ValueError("token is required")
        return cls(token_id=token_id, user_mail=user_mail, provider_id=provider_id, masked_token_label=mask_token(raw_token))

    def replace(self, raw_token: str) -> None:
        if not raw_token.strip():
            raise ValueError("token is required")
        self.masked_token_label = mask_token(raw_token)
        self.status = ProviderTokenStatusValue.CONFIGURED
        self.updated_at = _now()
