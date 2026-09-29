"""Fetch the models that a user's current provider credential can access."""

from dataclasses import dataclass
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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

        excluded_terms = ("audio", "embedding", "image", "moderation", "realtime", "transcribe", "tts", "whisper")
        models_by_id = {
            item["id"]: item.get("created", 0)
            for item in items
            if isinstance(item, dict)
            and isinstance(item.get("id"), str)
            and item["id"].startswith(("gpt-", "chatgpt-", "o1", "o3", "o4"))
            and not any(term in item["id"].lower() for term in excluded_terms)
        }
        model_ids = sorted(models_by_id, key=lambda model_id: models_by_id[model_id] if isinstance(models_by_id[model_id], int) else 0, reverse=True)
        return [AIModel(model_id, "openai", model_id, ModelAvailabilityStatus.AVAILABLE, ["API"]) for model_id in model_ids]


class GoogleModelsClient:
    def list_models(self, api_key: str) -> list[AIModel]:
        page_token = None
        result = []
        for _ in range(10):
            query = urlencode({"pageToken": page_token}) if page_token else ""
            url = "https://generativelanguage.googleapis.com/v1beta/models" + (f"?{query}" if query else "")
            request = Request(url, headers={"x-goog-api-key": api_key})
            payload = _get_json(request, "Google AI")
            items = payload.get("models")
            if not isinstance(items, list):
                raise ProviderModelsUnavailableError("Google AI devolvió una lista de modelos inválida.")
            for item in items:
                methods = item.get("supportedGenerationMethods") if isinstance(item, dict) else None
                if not isinstance(methods, list) or "generateContent" not in methods:
                    continue
                name = item.get("name")
                if isinstance(name, str) and name.startswith("models/"):
                    model_id = name.removeprefix("models/")
                    result.append(AIModel(model_id, "google", item.get("displayName") or model_id, ModelAvailabilityStatus.AVAILABLE, ["API", "chat"]))
            page_token = payload.get("nextPageToken")
            if not page_token:
                break
        return result


class AnthropicModelsClient:
    def list_models(self, api_key: str) -> list[AIModel]:
        after_id = None
        result = []
        for _ in range(10):
            query = urlencode({"limit": 1000, **({"after_id": after_id} if after_id else {})})
            request = Request(
                f"https://api.anthropic.com/v1/models?{query}",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            )
            payload = _get_json(request, "Anthropic")
            items = payload.get("data")
            if not isinstance(items, list):
                raise ProviderModelsUnavailableError("Anthropic devolvió una lista de modelos inválida.")
            for item in items:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    result.append(AIModel(item["id"], "anthropic", item.get("display_name") or item["id"], ModelAvailabilityStatus.AVAILABLE, ["API", "chat"]))
            after_id = payload.get("last_id")
            if not payload.get("has_more") or not after_id:
                break
        return result


def _get_json(request: Request, provider_name: str) -> dict:
    try:
        with urlopen(request, timeout=10) as response:  # nosec B310: fixed provider model-catalog endpoints
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code in {400, 401, 403}:
            raise ProviderModelsUnavailableError(f"La clave de {provider_name} no es válida o no tiene acceso al catálogo de modelos.") from error
        raise ProviderModelsUnavailableError(f"{provider_name} no pudo entregar sus modelos en este momento.") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ProviderModelsUnavailableError(f"No se pudieron consultar los modelos de {provider_name}.") from error
    if not isinstance(payload, dict):
        raise ProviderModelsUnavailableError(f"{provider_name} devolvió una respuesta de catálogo inválida.")
    return payload


class ListAvailableModels:
    def __init__(self, providers: AIProviderRepository, models: AIModelRepository, tokens: ProviderTokenRepository, openai: OpenAIModelsClient | None = None, google: GoogleModelsClient | None = None, anthropic: AnthropicModelsClient | None = None):
        self.providers = providers
        self.models = models
        self.tokens = tokens
        self.openai = openai or OpenAIModelsClient()
        self.google = google or GoogleModelsClient()
        self.anthropic = anthropic or AnthropicModelsClient()

    def execute(self, user_mail: str, provider_id: str) -> AvailableModelList:
        provider = self.providers.get(provider_id)
        if provider is None:
            raise ProviderModelsUnavailableError("Proveedor no encontrado.")

        secret = self.tokens.get_secret(user_mail, provider_id)
        clients = {"openai": self.openai, "google": self.google, "anthropic": self.anthropic}
        if secret and provider_id in clients:
            client = clients[provider_id]
            available = client.list_models(secret)
            if not available:
                raise ProviderModelsUnavailableError(f"El token de {provider.name} se guardó, pero la API no devolvió modelos compatibles para generar texto.")
            return AvailableModelList(provider_id, "token", "Modelos habilitados para tu token actual.", available)

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
