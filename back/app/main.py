import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.user.auth_routes import router as auth_router
from app.presentation.user.profile_routes import router as profile_router
from app.presentation.user.technical_profile_routes import router as technical_profile_router
from app.presentation.user.usage_routes import router as usage_router
from app.presentation.chat_routes import router as chat_router
from app.infrastructure.database import get_database


def create_app() -> FastAPI:
    app = FastAPI(title="Modulo de Usuario API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router)
    app.include_router(profile_router)
    app.include_router(technical_profile_router)
    app.include_router(usage_router)
    app.include_router(chat_router)

    @app.middleware("http")
    async def private_responses(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/health")
    def health(database=Depends(get_database)):
        from fastapi.responses import JSONResponse
        result = database.health()
        return JSONResponse({"database": result}, status_code=200 if result["ok"] else 503)

    return app


app = create_app()
