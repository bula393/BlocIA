"""Wire HTTP modules without coupling them to the process entry point."""

import asyncio
from contextlib import asynccontextmanager
import logging
import os
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.application.chat.inference_client import close_inference_client
from app.infrastructure.runtime_settings import RuntimeSettings
from app.presentation.chat_routes import router as chat_router
from app.presentation.health_routes import router as health_router
from app.presentation.user.auth_routes import router as auth_router
from app.presentation.user.profile_routes import router as profile_router
from app.presentation.user.technical_profile_routes import router as technical_profile_router
from app.presentation.user.usage_routes import router as usage_router
from app.presentation.user.google_ai_routes import router as google_ai_router


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
    app.state.runtime_settings = config
    app.add_middleware(CORSMiddleware, allow_origins=[config.frontend_url], allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])
    for router in (health_router, auth_router, profile_router, technical_profile_router, google_ai_router, usage_router, chat_router):
        app.include_router(router)

    @app.middleware("http")
    async def block_cross_origin_cookie_mutations(request: Request, call_next):
        unsafe = request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}
        if unsafe and request.cookies.get("bloqia_session"):
            origin = request.headers.get("origin")
            if origin is None and config.production:
                return JSONResponse({"detail": {"message": "Origin header required for cookie-authenticated requests."}}, status_code=403)
            if origin is not None:
                try:
                    supplied = urlsplit(origin)
                    expected = urlsplit(config.frontend_url)
                    supplied_port = supplied.port or (443 if supplied.scheme == "https" else 80)
                    expected_port = expected.port or (443 if expected.scheme == "https" else 80)
                    matches = (
                        supplied.scheme in {"http", "https"}
                        and supplied.scheme == expected.scheme
                        and supplied.hostname is not None
                        and supplied.hostname.lower() == (expected.hostname or "").lower()
                        and supplied_port == expected_port
                        and supplied.username is None
                        and supplied.password is None
                        and supplied.path in {"", "/"}
                        and not supplied.query
                        and not supplied.fragment
                    )
                except ValueError:
                    matches = False
                if not matches:
                    return JSONResponse({"detail": {"message": "Origin not allowed for cookie-authenticated requests."}}, status_code=403)
        return await call_next(request)

    @app.middleware("http")
    async def private_responses(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    return app
