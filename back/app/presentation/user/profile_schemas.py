from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    mail: EmailStr
    age: int = Field(ge=1)
    profession: str
    displayName: str | None = None
    loginProviderStatus: str
    technicalProfileStatus: str


class ProfileUpdateRequest(BaseModel):
    age: int | None = Field(default=None, ge=1)
    profession: str | None = Field(default=None, min_length=1)
    displayName: str | None = None
