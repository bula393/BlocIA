from dataclasses import dataclass, field

from .enums import ModelAvailabilityStatus


@dataclass
class AIModel:
    model_id: str
    provider_id: str
    display_name: str
    availability_status: ModelAvailabilityStatus = ModelAvailabilityStatus.AVAILABLE
    capabilities: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.provider_id:
            raise ValueError("Every model must belong to a provider")
        if not self.display_name.strip():
            raise ValueError("Model display name must be visible")
