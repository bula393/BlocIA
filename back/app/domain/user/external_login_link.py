from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ExternalLoginLink:
    user_mail: str
    provider: str
    external_subject: str
    provided_mail: str
    provided_display_name: str | None = None
    created_at: datetime = field(default_factory=_now)
    last_used_at: datetime | None = None

    def mark_used(self) -> None:
        self.last_used_at = _now()
