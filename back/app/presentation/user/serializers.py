from app.domain.user.ai_model import AIModel
from app.domain.user.ai_provider import AIProvider
from app.domain.user.provider_token import ProviderToken
from app.domain.user.user import User


def user_profile(user: User) -> dict:
    return {
        "mail": user.mail,
        "age": user.age,
        "profession": user.profession,
        "displayName": user.display_name,
        "loginProviderStatus": user.login_provider_status.value,
        "technicalProfileStatus": user.technical_profile_status.value,
    }


def token_status(provider_id: str, status: str, token: ProviderToken | None = None) -> dict:
    return {
        "providerId": provider_id,
        "status": status,
        "maskedTokenLabel": token.masked_token_label if token else None,
        "lastValidatedAt": token.last_validated_at.isoformat() if token and token.last_validated_at else None,
    }


def model_schema(model: AIModel) -> dict:
    return {
        "modelId": model.model_id,
        "displayName": model.display_name,
        "availabilityStatus": model.availability_status.value,
        "capabilities": model.capabilities,
    }


def provider_schema(provider: AIProvider, models: list[AIModel], status: dict) -> dict:
    return {
        "providerId": provider.provider_id,
        "name": provider.name,
        "status": provider.status.value,
        "description": provider.description,
        "tokenStatus": status,
        "models": [model_schema(model) for model in models],
    }
