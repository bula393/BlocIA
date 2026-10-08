"""Private inference application, independent of user data and provider credentials."""

import asyncio
from contextlib import asynccontextmanager
import logging
import os
import secrets
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.infrastructure.dev_environment import load_dev_environment
from app.application.chat.ai_responder import LocalTextModel
from app.application.chat.free_models import LOCAL_MODEL_ID
from app.application.chat.local_models import LocalModels
from app.application.chat.settings import settings


load_dev_environment()

MAX_GENERATION_CHARACTERS = 20_000


class ClassifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=12_000)


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=MAX_GENERATION_CHARACTERS)
    modelId: Literal["qwen3-local"] = LOCAL_MODEL_ID


class WarmupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    includeGeneration: bool = False


def create_app(classifier=None, generator=None):
    token = os.getenv("BLOCIA_INFERENCE_TOKEN", "").strip()
    if os.getenv("ENVIRONMENT", "development").strip().lower() == "production" and not token:
        raise ValueError("BLOCIA_INFERENCE_TOKEN es obligatorio para el servicio de IA en producción.")
    # Do not use the factories: they may point back to this same service.
    classifier = LocalModels() if classifier is None else classifier
    generator = LocalTextModel() if generator is None else generator
    generation_enabled = os.getenv("BLOCIA_ENABLE_LOCAL_CHAT", "1").strip() != "0"

    @asynccontextmanager
    async def lifespan(app):
        try:
            if os.getenv("BLOCIA_PRELOAD_CLASSIFIER", "1") == "1":
                await asyncio.to_thread(classifier.warmup)
            if generation_enabled and os.getenv("BLOCIA_PRELOAD_LOCAL_CHAT", "0") == "1":
                await asyncio.to_thread(generator.warmup)
        except Exception as error:
            logging.getLogger(__name__).warning("Inference model warmup unavailable: %s", type(error).__name__)
        yield

    app = FastAPI(title="BlocIA inference", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.state.classifier = classifier
    app.state.generator = generator

    def authenticate(x_inference_token: str | None = Header(default=None)):
        if token and not secrets.compare_digest((x_inference_token or "").encode(), token.encode()):
            raise HTTPException(401, detail={"message": "No se pudo autenticar la solicitud de inferencia."})

    @app.middleware("http")
    async def private_responses(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, error):
        # Pydantic's default validation body includes the rejected user input.
        return JSONResponse({"detail": {"message": "Solicitud de inferencia inválida."}}, status_code=422)

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/ready")
    def ready():
        try:
            available = bool(classifier.status().get("classifierReady", False))
        except Exception:
            available = False
        return JSONResponse({"ready": available, "classifierReady": available}, status_code=200 if available else 503)

    @app.get("/status", dependencies=[Depends(authenticate)])
    def status():
        try:
            return {**classifier.status(), "release": os.getenv("RELEASE_TAG", "development")}
        except Exception:
            raise HTTPException(503, detail={"message": "No se pudo consultar el estado del servicio de IA."}) from None

    @app.post("/classify", dependencies=[Depends(authenticate)])
    def classify(payload: ClassifyRequest):
        _, chat_config = settings()
        if not payload.prompt.strip() or len(payload.prompt) > chat_config.max_input_characters:
            raise HTTPException(422, detail={"message": f"La consulta admite entre 1 y {chat_config.max_input_characters} caracteres."})
        try:
            return classifier.classify(payload.prompt)
        except Exception:
            raise HTTPException(503, detail={"message": "El clasificador de IA no está disponible. Intentá de nuevo."}) from None

    @app.post("/generate", dependencies=[Depends(authenticate)])
    def generate(payload: GenerateRequest):
        if not generation_enabled:
            raise HTTPException(503, detail={"message": "El modelo local de chat no está habilitado."})
        if not payload.prompt.strip():
            raise HTTPException(422, detail={"message": "Escribí una consulta antes de enviarla."})
        try:
            answer = generator.generate(payload.prompt)
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("Empty generation")
            return {"answer": answer.strip()}
        except Exception:
            raise HTTPException(503, detail={"message": "El modelo de IA no pudo generar una respuesta. Intentá de nuevo."}) from None

    @app.post("/warmup", dependencies=[Depends(authenticate)])
    def warmup(payload: WarmupRequest | None = None):
        if payload and payload.includeGeneration and not generation_enabled:
            raise HTTPException(503, detail={"message": "El modelo local de chat no está habilitado."})
        try:
            classifier.warmup()
            if payload and payload.includeGeneration:
                generator.warmup()
            return classifier.status()
        except Exception:
            raise HTTPException(503, detail={"message": "No se pudieron preparar los modelos de IA."}) from None

    return app


app = create_app()
