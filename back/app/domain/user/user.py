from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parseaddr

from .enums import LoginProviderStatus, TechnicalProfileStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


def is_valid_email(mail: str) -> bool:
    parsed = parseaddr(mail or "")[1]
    return bool(parsed and "@" in parsed and parsed == mail)


@dataclass
class User:
    mail: str
    age: int
    profession: str
    password_status: bool = False
    display_name: str | None = None
    login_provider_status: LoginProviderStatus = LoginProviderStatus.PASSWORD
    technical_profile_status: TechnicalProfileStatus = TechnicalProfileStatus.NOT_CONFIGURED
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def validate(self) -> None:
        if not is_valid_email(self.mail):
            raise ValueError("mail must be present, valid, and unique")
        if self.age <= 0:
            raise ValueError("age must be present and positive")
        if not self.profession.strip():
            raise ValueError("profession must be present before registration completes")

    def update_profile(self, age: int | None = None, profession: str | None = None, display_name: str | None = None) -> None:
        if age is not None:
            if age <= 0:
                raise ValueError("age must be present and positive")
            self.age = age
        if profession is not None:
            if not profession.strip():
                raise ValueError("profession must be present before registration completes")
            self.profession = profession
        if display_name is not None:
            self.display_name = display_name
        self.updated_at = _now()
