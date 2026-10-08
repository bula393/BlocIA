import logging
from functools import lru_cache
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from app.application.chat.ai_responder import AIResponder
from app.application.chat.default_provider_tokens import default_provider_token
from app.application.chat.free_models import LOCAL_MODEL_ID, local_free_models
from app.application.chat.google_defaults import default_google_key, default_google_models
from app.application.chat.google_model_access import google_quota_models, UNVERIFIED_GOOGLE_QUOTA
from app.application.chat.remote_defaults import default_openrouter_key, remote_free_models
from app.application.chat.local_models import local_models, ModelUnavailableError
from app.application.chat.settings import settings
from app.infrastructure.chat_repository import ChatRepository, ConversationNotFoundError, TurnConflictError
from app.infrastructure.usage_analytics_repository import LIMIT_REASONS, UsageAnalyticsRepository
from app.infrastructure.database import get_database
from app.presentation.user.dependencies import current_user_mail, provider_repo, token_repo, user_repo

from app.application.chat.send_message import send_chat_message, UsageBlockedError
from app.presentation.chat_schemas import SendMessage

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


def chat_repository(database=Depends(get_database)):
    return ChatRepository(database)


def chat_user(mail=Depends(current_user_mail), users=Depends(user_repo)):
    if not users.exists(mail):
        raise HTTPException(401, detail={"message": "Volvé a iniciar sesión."})
    return mail


@lru_cache(maxsize=1)
def ai_responder():
    return AIResponder()


def not_found(error):
    return HTTPException(404, detail={"message": str(error)})


def lock_message(usage_lock):
    reasons = [LIMIT_REASONS[reason] for reason in usage_lock["reasonCodes"] if reason in LIMIT_REASONS]
    minutes = usage_lock.get("lockDurationMinutes", 1440)
    if minutes % 60 == 0:
        hours = minutes // 60
        duration = f"{hours} {'hora' if hours == 1 else 'horas'}"
    else:
        duration = f"{minutes} {'minuto' if minutes == 1 else 'minutos'}"
    return " ".join([*reasons, f"La IA está bloqueada durante {duration}."])


@router.get("/status")
def status(mail=Depends(chat_user), models=Depends(local_models), repository=Depends(chat_repository)):
    result = models.status()
    # A global key uses its live catalog. Do not advertise the legacy fixed
    # Google model, whose access was verified against a different credential.
    google_models = [] if default_provider_token("google") else default_google_models()
    if google_models:
        allowed = google_quota_models(default_google_key())
        google_models = [model for model in google_models if model.get("modelId") in allowed]
    usage_lock = UsageAnalyticsRepository(repository.database).current_lock(mail)
    return {**result, "freeModels": google_models + remote_free_models() + result.get("freeModels", []), "usageLock": usage_lock}


@router.get("/conversations")
def list_conversations(mail=Depends(chat_user), repository=Depends(chat_repository)):
    return {"conversations": repository.list(mail)}


@router.post("/conversations", status_code=201)
def create_conversation(mail=Depends(chat_user), repository=Depends(chat_repository)):
    return repository.create(mail)


@router.get("/conversations/{identifier}")
def read_conversation(identifier: UUID, mail=Depends(chat_user), repository=Depends(chat_repository)):
    try:
        return {"conversation": repository.get(mail, str(identifier)), "messages": repository.messages(mail, str(identifier))}
    except ConversationNotFoundError as error:
        raise not_found(error)


@router.get("/conversations/{identifier}/messages/{request_id}/progress")
def message_progress(identifier: UUID, request_id: UUID, mail=Depends(chat_user), repository=Depends(chat_repository)):
    try:
        progress = repository.progress(mail, str(identifier), str(request_id))
        if progress is None:
            raise HTTPException(404, detail={"message": "No se encontró el envío."})
        return progress
    except ConversationNotFoundError as error:
        raise not_found(error)


@router.delete("/conversations/{identifier}", status_code=204)
def delete_conversation(identifier: UUID, mail=Depends(chat_user), repository=Depends(chat_repository)):
    try:
        repository.delete(mail, str(identifier))
        return Response(status_code=204)
    except ConversationNotFoundError as error:
        raise not_found(error)


@router.post("/conversations/{identifier}/messages")
def send_message(identifier: UUID, payload: SendMessage, response: Response, mail=Depends(chat_user), repository=Depends(chat_repository), models=Depends(local_models), providers=Depends(provider_repo), tokens=Depends(token_repo), users=Depends(user_repo), responder=Depends(ai_responder)):
    identifier, request_id = str(identifier), str(payload.requestId)
    usage_analytics = UsageAnalyticsRepository(repository.database)
    try:
        completed = repository.is_completed(mail, identifier, request_id, payload.prompt)
    except ConversationNotFoundError as error:
        raise not_found(error)
    except TurnConflictError as error:
        raise HTTPException(409, detail={"message": str(error)})
    usage_lock = usage_analytics.current_lock(mail)
    if completed:
        return {"conversation": repository.get(mail, identifier), "messages": repository.messages(mail, identifier), "usageLock": usage_lock}
    if usage_lock["blocked"]:
        raise HTTPException(423, detail={"message": lock_message(usage_lock), "usageLock": usage_lock})
    _, config = settings()
    if len(payload.prompt) > config.max_input_characters:
        raise HTTPException(422, detail={"message": f"La consulta admite hasta {config.max_input_characters} caracteres."})
    api_key = None
    if payload.providerId:
        if payload.providerId == "local":
            if payload.modelId != LOCAL_MODEL_ID or not local_free_models():
                raise HTTPException(422, detail={"message": "El modelo local gratuito no está instalado."})
        else:
            provider = providers.get(payload.providerId)
            if payload.providerId not in responder.supported_providers or provider is None or provider.status.value != "available":
                raise HTTPException(422, detail={"message": "El proveedor elegido no está disponible."})
            api_key = tokens.get_secret(mail, payload.providerId)
            if not api_key:
                api_key = default_provider_token(payload.providerId)
            if not api_key and payload.providerId == "google":
                api_key = default_google_key()
            elif not api_key and payload.providerId == "openrouter":
                api_key = default_openrouter_key()
            if payload.providerId == "google" and api_key:
                allowed = google_quota_models(api_key)
                if payload.modelId not in allowed:
                    message = UNVERIFIED_GOOGLE_QUOTA if not allowed else "Este modelo no tiene cuota de texto habilitada en el proyecto de tu clave Google. Actualizá el selector y elegí uno de los modelos habilitados."
                    raise HTTPException(422, detail={"message": message})
    try:
        result = send_chat_message(mail, identifier, request_id, payload, repository=repository, models=models,
                                   users=users, responder=responder, usage_analytics=usage_analytics, api_key=api_key)
        if result.get("confirmationRequired"):
            response.status_code = 202
        return result
    except UsageBlockedError as error:
        raise HTTPException(423, detail={"message": lock_message(error.usage_lock), "usageLock": error.usage_lock})
    except HTTPException:
        raise
    except ConversationNotFoundError as error:
        raise not_found(error)
    except TurnConflictError as error:
        raise HTTPException(409, detail={"message": str(error)})
    except (ModelUnavailableError) as error:
        raise HTTPException(503, detail={"message": str(error)})
    except ValueError as error:
        raise HTTPException(422, detail={"message": str(error)})
    except Exception as error:
        # Never log prompt text, personal identifiers, or model inputs.
        logger.error("Local chat failed: %s", type(error).__name__)
        raise HTTPException(503, detail={"message": "No se pudo clasificar la consulta. Podés reintentar el envío."}) from error
