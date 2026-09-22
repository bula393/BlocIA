"""Fetch the models that a user's current provider credential can access."""

from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.domain.user.ai_model import AIModel
from app.domain.user.enums import ModelAvailabilityStatus
from app.domain.user.repositories import AIModelRepository, AIProviderRepository, ProviderTokenRepository


class ProviderModelsUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class AvailableModelList:
    provider_id: str
    source: str
    message: str
    models: list[AIModel]


# These weights are free to download and run, but are not free OpenAI API calls.
OPEN_WEIGHT_MODELS = [
    AIModel("gpt-oss-20b", "openai", "gpt-oss-20b", ModelAvailabilityStatus.AVAILABLE, ["texto", "pesos abiertos", "requiere ejecucion local"]),
    AIModel("gpt-oss-120b", "openai", "gpt-oss-120b", ModelAvailabilityStatus.AVAILABLE, ["texto", "pesos abiertos", "requiere ejecucion local"]),
]


class OpenAIModelsClient:
    """Tiny HTTP client so the API key never leaves the backend."""

    def list_models(self, api_key: str) -> list[AIModel]:
        request = Request(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        try:
            with urlopen(request, timeout=10) as response:  # nosec B310: fixed OpenAI API endpoint
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code in {401, 403}:
                raise ProviderModelsUnavailableError("El token de OpenAI no es valido o no tiene acceso a modelos.") from error
            raise ProviderModelsUnavailableError("OpenAI no pudo entregar los modelos en este momento.") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ProviderModelsUnavailableError("No se pudieron consultar los modelos de OpenAI.") from error

        items = payload.get("data")
        if not isinstance(items, list):
            raise ProviderModelsUnavailableError("OpenAI devolvio una lista de modelos invalida.")

        models_by_id = {
            item["id"]: item.get("created", 0)
            for item in items
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        model_ids = sorted(models_by_id, key=lambda model_id: models_by_id[model_id] if isinstance(models_by_id[model_id], int) else 0, reverse=True)
        return [AIModel(model_id, "openai", model_id, ModelAvailabilityStatus.AVAILABLE, ["API"]) for model_id in model_ids]


class ListAvailableModels:
    def __init__(self, providers: AIProviderRepository, models: AIModelRepository, tokens: ProviderTokenRepository, openai: OpenAIModelsClient | None = None):
        self.providers = providers
        self.models = models
        self.tokens = tokens
        self.openai = openai or OpenAIModelsClient()

    def execute(self, user_mail: str, provider_id: str) -> AvailableModelList:
        provider = self.providers.get(provider_id)
        if provider is None:
            raise ProviderModelsUnavailableError("Proveedor no encontrado.")

        secret = self.tokens.get_secret(user_mail, provider_id)
        if secret and provider_id == "openai":
            return AvailableModelList(provider_id, "token", "Modelos habilitados para tu token actual.", self.openai.list_models(secret))

        if provider_id == "openai":
            return AvailableModelList(
                provider_id,
                "free",
                "Sin token no hay modelos de la API de OpenAI. Estos son modelos open-weight gratuitos para ejecutar localmente.",
                OPEN_WEIGHT_MODELS,
            )

        return AvailableModelList(
            provider_id,
            "catalog",
            "Catalogo del proveedor. Configura su token para validar el acceso de tu cuenta.",
            self.models.list_by_provider(provider_id),
        )
