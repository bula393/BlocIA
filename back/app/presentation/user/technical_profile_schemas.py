from pydantic import BaseModel, Field


class ProviderTokenSaveRequest(BaseModel):
    providerId: str
    token: str = Field(min_length=1)


class ProviderTokenStatus(BaseModel):
    providerId: str
    status: str
    maskedTokenLabel: str | None = None
    lastValidatedAt: str | None = None


class AIModelSchema(BaseModel):
    modelId: str
    displayName: str
    availabilityStatus: str
    capabilities: list[str] = []


class ProviderWithModels(BaseModel):
    providerId: str
    name: str
    status: str
    tokenStatus: ProviderTokenStatus
    models: list[AIModelSchema]
