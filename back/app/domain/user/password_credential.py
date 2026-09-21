from dataclasses import dataclass, field
from datetime import datetime, timezone

from .password_policy import PasswordPolicy


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class PasswordCredential:
    user_mail: str
    password_hash: str
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    @classmethod
    def create(cls, user_mail: str, raw_password: str) -> "PasswordCredential":
        PasswordPolicy.validate(raw_password, user_mail)
        return cls(user_mail=user_mail, password_hash=PasswordPolicy.hash_password(raw_password))

    def verify(self, raw_password: str) -> bool:
        return PasswordPolicy.verify(raw_password, self.password_hash)

    def register_invalid_attempt(self) -> None:
        return None
