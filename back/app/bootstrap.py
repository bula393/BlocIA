"""Wire HTTP modules without coupling them to the process entry point."""

import asyncio
from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.application.chat.inference_client import close_inference_client
from app.infrastructure.runtime_settings import RuntimeSettings
from app.presentation.chat_routes import router as chat_router
from app.presentation.health_routes import router as health_router
from app.presentation.user.auth_routes import router as auth_router
from app.presentation.user.profile_routes import router as profile_router
from app.presentation.user.technical_profile_routes import router as technical_profile_router
from app.presentation.user.usage_routes import router as usage_router


@asynccontextmanager
async def application_lifespan(classifier_factory, text_factory, responder_factory):
    try:
        if os.getenv("BLOCIA_PRELOAD_CLASSIFIER", "1") == "1":
            await asyncio.to_thread(classifier_factory().warmup)
        if os.getenv("BLOCIA_PRELOAD_LOCAL_CHAT", "0") == "1":
            await asyncio.to_thread(text_factory().warmup)
    except Exception as error:
        logging.getLogger(__name__).warning("Chat model warmup unavailable: %s", type(error).__name__)
    try:
        yield
    finally:
        try:
            responder_factory().close()
        finally:
            close_inference_client()


def create_application(lifespan):
    config = RuntimeSettings.from_environment()
    app = FastAPI(title="BlocIA API", version="0.1.0", lifespan=lifespan,
                  docs_url=None if config.production else "/docs",
                  redoc_url=None if config.production else "/redoc")
    app.add_middleware(CORSMiddleware, allow_origins=[config.frontend_url], allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])
    for router in (health_router, auth_router, profile_router, technical_profile_router, usage_router, chat_router):
        app.include_router(router)

    @app.middleware("http")
    async def private_responses(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    return app
