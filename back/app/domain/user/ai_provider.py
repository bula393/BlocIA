from dataclasses import dataclass

from .enums import ProviderStatus


@dataclass
class AIProvider:
    provider_id: str
    name: str
    status: ProviderStatus = ProviderStatus.AVAILABLE
    description: str | None = None

    def can_accept_token(self) -> bool:
        return self.status == ProviderStatus.AVAILABLE

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Provider name must be visible to users")
