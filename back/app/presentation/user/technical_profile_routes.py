from fastapi import APIRouter, Depends, Response

from app.application.user.list_technical_providers import ListTechnicalProviders
from app.application.user.list_available_models import ListAvailableModels, ProviderModelsUnavailableError
from app.application.user.remove_provider_token import RemoveProviderToken
from app.application.user.save_provider_token import ProviderUnavailableError, SaveProviderToken
from .dependencies import current_user_mail, model_repo, provider_repo, token_repo, usage_repo
from .errors import error_response, validation_error_response
from .serializers import provider_schema, token_status
from .technical_profile_schemas import ProviderTokenSaveRequest
from app.domain.user.usage_event import UsageEvent

router = APIRouter(tags=["TechnicalProfile"])


@router.get("/technical-profile/providers")
def list_providers(mail: str = Depends(current_user_mail), providers=Depends(provider_repo), models=Depends(model_repo), tokens=Depends(token_repo)):
    rows = ListTechnicalProviders(providers, models, tokens).execute(mail)
    return {"providers": [provider_schema(row["provider"], row["models"], token_status(row["provider"].provider_id, row["token_status"].value, row["token"])) for row in rows]}


@router.get("/technical-profile/providers/{provider_id}/models")
def list_available_models(provider_id: str, mail: str = Depends(current_user_mail), providers=Depends(provider_repo), models=Depends(model_repo), tokens=Depends(token_repo), usage=Depends(usage_repo)):
    try:
        result = ListAvailableModels(providers, models, tokens).execute(mail, provider_id)
        usage.record(UsageEvent(mail, "model_catalog_requested", provider_id))
        return {
            "providerId": result.provider_id,
            "source": result.source,
            "message": result.message,
            "models": [
                {
                    "modelId": model.model_id,
                    "displayName": model.display_name,
                    "availabilityStatus": model.availability_status.value,
                    "capabilities": model.capabilities,
                }
                for model in result.models
            ],
        }
    except ProviderModelsUnavailableError as exc:
        raise error_response(str(exc), 502)


@router.post("/technical-profile/tokens")
def save_token(payload: ProviderTokenSaveRequest, mail: str = Depends(current_user_mail), providers=Depends(provider_repo), tokens=Depends(token_repo), usage=Depends(usage_repo)):
    try:
        token = SaveProviderToken(providers, tokens).execute(mail, payload.providerId, payload.token)
        usage.record(UsageEvent(mail, "provider_token_saved", payload.providerId))
        return token_status(token.provider_id, token.status.value, token)
    except ProviderUnavailableError as exc:
        raise validation_error_response(str(exc), {"providerId": str(exc)})
    except ValueError as exc:
        raise validation_error_response(str(exc), {"token": str(exc)})


@router.delete("/technical-profile/tokens/{provider_id}", status_code=204)
def remove_token(provider_id: str, mail: str = Depends(current_user_mail), tokens=Depends(token_repo), usage=Depends(usage_repo)):
    removed = RemoveProviderToken(tokens).execute(mail, provider_id)
    if not removed:
        raise error_response("Provider token not configured for current user", 404)
    usage.record(UsageEvent(mail, "provider_token_removed", provider_id))
    return Response(status_code=204)
