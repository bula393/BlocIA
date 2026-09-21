from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    mail: EmailStr
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    mail: EmailStr
    password: str = Field(min_length=10)
    age: int = Field(ge=1)
    profession: str = Field(min_length=1)


class GoogleRegistrationCompletionRequest(BaseModel):
    registrationToken: str
    age: int = Field(ge=1)
    profession: str = Field(min_length=1)


class RegistrationCompletionRequiredResponse(BaseModel):
    registrationToken: str
    missingFields: list[str]
    prefilledFields: dict


class AuthSessionResponse(BaseModel):
    user: dict
    accessToken: str
    expiresInSeconds: int
