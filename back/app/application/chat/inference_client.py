"""Private HTTP transport for the optional, separately deployed inference service."""

from functools import lru_cache
import math
import os
from threading import RLock
from urllib.parse import urlsplit

import httpx


CLASSIFICATION_TIMEOUT_SECONDS = 30
DEFAULT_GENERATION_TIMEOUT_SECONDS = 300


def inference_url():
    return os.getenv("BLOCIA_INFERENCE_URL", "").strip().rstrip("/")


def generation_timeout_seconds():
    try:
        value = float(os.getenv("BLOCIA_INFERENCE_TIMEOUT_SECONDS", str(DEFAULT_GENERATION_TIMEOUT_SECONDS)))
    except ValueError:
        return DEFAULT_GENERATION_TIMEOUT_SECONDS
    return value if math.isfinite(value) and value > 0 else DEFAULT_GENERATION_TIMEOUT_SECONDS


class InferenceUnavailableError(RuntimeError):
    pass


class InferenceClient:
    def __init__(self, url=None, token=None, client: httpx.Client | None = None):
        self._url = (inference_url() if url is None else url).rstrip("/")
        try:
            parsed = urlsplit(self._url)
            parsed.port  # Validate the port before constructing an outgoing request.
        except ValueError:
            raise ValueError("Configurá una dirección HTTP válida para el servicio de IA.") from None
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username
                or parsed.password or parsed.query or parsed.fragment):
            raise ValueError("Configurá una dirección HTTP válida para el servicio de IA.")
        self._token = os.getenv("BLOCIA_INFERENCE_TOKEN", "").strip() if token is None else token
        if os.getenv("ENVIRONMENT", "development").strip().lower() == "production" and not self._token:
            raise ValueError("BLOCIA_INFERENCE_TOKEN es obligatorio para el servicio de IA en producción.")
        self._client = client
        self._client_lock = RLock()

    def _http_client(self):
        with self._client_lock:
            if self._client is None:
                self._client = httpx.Client(
                    timeout=httpx.Timeout(CLASSIFICATION_TIMEOUT_SECONDS, connect=5, pool=5),
                    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5, keepalive_expiry=120),
                    follow_redirects=False,
                    trust_env=False,
                )
            return self._client

    def close(self):
        with self._client_lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    def _request(self, method, path, body=None, timeout_seconds=CLASSIFICATION_TIMEOUT_SECONDS):
        try:
            headers = {"X-Inference-Token": self._token} if self._token else {}
            request = httpx.Request(method, self._url + path, headers=headers, json=body)
            request.extensions["timeout"] = httpx.Timeout(timeout_seconds, connect=5, pool=5).as_dict()
            response = self._http_client().send(request)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Invalid inference response")
            return payload
        except (httpx.TimeoutException, TimeoutError):
            raise InferenceUnavailableError("El servicio de IA tardó demasiado en responder. Intentá de nuevo.") from None
        except (httpx.HTTPError, ValueError, UnicodeError):
            # Remote errors may echo a prompt or token. Never expose or log them.
            raise InferenceUnavailableError("No se pudo conectar con el servicio de IA o leer su respuesta. Intentá de nuevo.") from None

    def status(self):
        try:
            payload = self._request("GET", "/status")
            if (not isinstance(payload.get("ready"), bool) or not isinstance(payload.get("classifierReady"), bool)
                    or not isinstance(payload.get("freeModels", []), list)):
                raise InferenceUnavailableError("El servicio de IA devolvió un estado inválido.")
            return payload
        except InferenceUnavailableError:
            from .settings import settings
            _, chat_config = settings()
            return {"ready": False, "classifierReady": False, "mode": "classification",
                    "maxInputCharacters": chat_config.max_input_characters,
                    "freeModels": [], "inferenceAvailable": False}

    def classify(self, prompt):
        from .local_models import ModelUnavailableError
        try:
            payload = self._request("POST", "/classify", {"prompt": prompt})
            if (payload.get("label") not in {"no_personal", "personal_informativa", "personal_decision"}
                    or not isinstance(payload.get("confidence"), (int, float))
                    or not 0 <= payload["confidence"] <= 1
                    or not isinstance(payload.get("group"), str)
                    or not isinstance(payload.get("status"), str)
                    or not isinstance(payload.get("needs_human_review"), bool)):
                raise InferenceUnavailableError("El servicio de IA devolvió una clasificación inválida.")
            return payload
        except InferenceUnavailableError as error:
            raise ModelUnavailableError(str(error)) from None

    def warmup(self, include_generation=False):
        from .local_models import ModelUnavailableError
        try:
            return self._request(
                "POST", "/warmup", {"includeGeneration": include_generation},
                timeout_seconds=generation_timeout_seconds() if include_generation else CLASSIFICATION_TIMEOUT_SECONDS,
            )
        except InferenceUnavailableError as error:
            raise ModelUnavailableError(str(error)) from None

    def generate(self, prompt):
        from .ai_responder import AIResponseUnavailableError
        from .free_models import LOCAL_MODEL_ID
        try:
            payload = self._request("POST", "/generate", {"prompt": prompt, "modelId": LOCAL_MODEL_ID},
                                    timeout_seconds=generation_timeout_seconds())
            answer = payload.get("answer")
            if not isinstance(answer, str) or not answer.strip():
                raise InferenceUnavailableError("El servicio de IA devolvió una respuesta vacía.")
            return answer.strip()
        except InferenceUnavailableError as error:
            raise AIResponseUnavailableError(str(error)) from None


class RemoteTextModel:
    def __init__(self, client):
        self._client = client

    def generate(self, prompt):
        return self._client.generate(prompt)

    def warmup(self):
        return self._client.warmup(include_generation=True)


@lru_cache(maxsize=1)
def inference_client():
    return InferenceClient()


def close_inference_client():
    if inference_client.cache_info().currsize:
        inference_client().close()
