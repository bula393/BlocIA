from dataclasses import dataclass, field
from datetime import datetime, timezone


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class UsageEvent:
    user_mail: str
    event_type: str
    provider_id: str | None = None
    occurred_at: datetime = field(default_factory=now_utc)
