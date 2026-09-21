from enum import StrEnum


class LoginProviderStatus(StrEnum):
    PASSWORD = "password"
    GOOGLE = "google"
    PASSWORD_AND_GOOGLE = "password-and-google"


class TechnicalProfileStatus(StrEnum):
    NOT_CONFIGURED = "not-configured"
    PARTIALLY_CONFIGURED = "partially-configured"
    CONFIGURED = "configured"
    REQUIRES_ATTENTION = "requires-attention"


class ProviderStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEPRECATED = "deprecated"


class ModelAvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEPRECATED = "deprecated"


class ProviderTokenStatusValue(StrEnum):
    NOT_CONFIGURED = "not-configured"
    CONFIGURED = "configured"
    INVALID = "invalid"
    REQUIRES_ATTENTION = "requires-attention"
