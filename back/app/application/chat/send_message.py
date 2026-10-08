"""Classify, confirm, generate and persist one idempotent chat turn."""

from app.application.chat.ai_responder import AIResponseUnavailableError
from app.application.chat.context import build_model_context
from app.application.chat.predefined_responses import predefined_response
from app.application.chat.privacy import redact_personal_data
from app.domain.user.usage_event import UsageEvent
from app.infrastructure.user.sqlite_repositories import UsageRepository


class UsageBlockedError(RuntimeError):
    def __init__(self, usage_lock):
        self.usage_lock = usage_lock
        super().__init__("Chat quota is blocked")


def send_chat_message(mail, identifier, request_id, payload, *, repository, models, users, responder,
                      usage_analytics, api_key):
    reserved = False
    try:
        with repository.database.transaction():
            usage_lock = usage_analytics.current_lock(mail)
            if usage_lock["blocked"]:
                raise UsageBlockedError(usage_lock)
            reserved = repository.reserve(mail, identifier, request_id, payload.prompt)
        if reserved:
            classification = models.classify(payload.prompt)
            if classification["label"] == "personal_informativa" and not payload.acceptPersonalResponse:
                return {"conversation": repository.get(mail, identifier),
                        "messages": repository.messages(mail, identifier), "confirmationRequired": True,
                        "classification": classification, "usageLock": usage_analytics.current_lock(mail)}
            prompt = redact_personal_data(payload.prompt)
            preset = predefined_response(payload.prompt)
            answer = preset[1] if preset else "Esta consulta fue clasificada como una decisión personal. Revisá su clasificación antes de avanzar."
            response_provider = response_model = None
            if preset is None and classification["label"] in {"no_personal", "personal_informativa"}:
                if not payload.providerId:
                    answer = "No hay un modelo de respuesta seleccionado. Elegí uno en el selector y volvé a enviar la consulta."
                elif payload.providerId != "local" and not api_key:
                    answer = "El proveedor elegido no tiene un token conectado. Conectalo desde tu perfil técnico y volvé a enviar la consulta."
                else:
                    try:
                        model_prompt = build_model_context(users.get(mail), payload.prompt, repository.recent_context(mail, identifier))
                        repository.mark_generating(identifier, request_id)
                        answer = responder.generate(payload.providerId, payload.modelId, model_prompt, api_key)
                        response_provider, response_model = payload.providerId, payload.modelId
                    except AIResponseUnavailableError as error:
                        answer = str(error)
            with repository.database.transaction():
                repository.complete(mail, identifier, request_id, prompt, answer, classification, response_provider, response_model)
                UsageRepository(repository.database).record(UsageEvent(mail, "chat_message_sent", response_provider))
                usage_lock = usage_analytics.apply_limits(mail)
            reserved = False
        return {"conversation": repository.get(mail, identifier), "messages": repository.messages(mail, identifier),
                "usageLock": usage_lock}
    finally:
        if reserved:
            repository.fail(identifier, request_id)
