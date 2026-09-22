from datetime import datetime, timezone

from app.domain.user.repositories import ProviderTokenRepository, UsageEventRepository
from app.domain.user.enums import ProviderTokenStatusValue


class GetUsageSummary:
    def __init__(self, tokens: ProviderTokenRepository, events: UsageEventRepository):
        self.tokens = tokens
        self.events = events

    def execute(self, user_mail: str) -> dict:
        today = datetime.now(timezone.utc).date()
        todays_events = [event for event in self.events.list_for_user(user_mail) if event.occurred_at.date() == today]
        last_activity = max((event.occurred_at for event in todays_events), default=None)
        return {
            "chatMessages": sum(event.event_type == "chat_message_sent" for event in todays_events),
            "modelCatalogRequests": sum(event.event_type == "model_catalog_requested" for event in todays_events),
            "configuredProviders": sum(token.status == ProviderTokenStatusValue.CONFIGURED for token in self.tokens.list_for_user(user_mail)),
            "lastActivityAt": last_activity.isoformat() if last_activity else None,
        }
