import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field, field_validator

from app.application.chat.local_models import local_models, ModelUnavailableError
from app.application.chat.privacy import redact_personal_data
from app.application.chat.settings import settings
from app.domain.user.usage_event import UsageEvent
from app.infrastructure.chat_repository import ChatRepository, ConversationNotFoundError, TurnConflictError
from app.infrastructure.database import get_database
from app.infrastructure.user.sqlite_repositories import UsageRepository
from app.presentation.user.dependencies import current_user_mail, user_repo

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


def chat_repository(database=Depends(get_database)):
    return ChatRepository(database)


def chat_user(mail=Depends(current_user_mail), users=Depends(user_repo)):
    if not users.exists(mail):
        raise HTTPException(401, detail={"message": "Volvé a iniciar sesión."})
    return mail


class SendMessage(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    requestId: UUID

    @field_validator("prompt")
    @classmethod
    def trim_prompt(cls, value):
        if not value.strip():
            raise ValueError("Escribí una consulta antes de enviarla.")
        return value.strip()


def not_found(error):
    return HTTPException(404, detail={"message": str(error)})


@router.get("/status")
def status(mail=Depends(chat_user), models=Depends(local_models)):
    return models.status()


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


@router.delete("/conversations/{identifier}", status_code=204)
def delete_conversation(identifier: UUID, mail=Depends(chat_user), repository=Depends(chat_repository)):
    try:
        repository.delete(mail, str(identifier))
        return Response(status_code=204)
    except ConversationNotFoundError as error:
        raise not_found(error)


@router.post("/conversations/{identifier}/messages")
def send_message(identifier: UUID, payload: SendMessage, mail=Depends(chat_user), repository=Depends(chat_repository), models=Depends(local_models)):
    identifier, request_id = str(identifier), str(payload.requestId)
    _, config = settings()
    if len(payload.prompt) > config.max_input_characters:
        raise HTTPException(422, detail={"message": f"La consulta admite hasta {config.max_input_characters} caracteres."})
    reserved = False
    try:
        reserved = repository.reserve(mail, identifier, request_id, payload.prompt)
        if reserved:
            classification = models.classify(payload.prompt)
            prompt = redact_personal_data(payload.prompt)
            result = json.dumps(classification, ensure_ascii=False)
            with repository.database.transaction():
                repository.complete(mail, identifier, request_id, prompt, result, classification)
                UsageRepository(repository.database).record(UsageEvent(mail, "chat_message_sent"))
        return {"conversation": repository.get(mail, identifier), "messages": repository.messages(mail, identifier)}
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
    finally:
        if reserved:
            repository.fail(identifier, request_id)
