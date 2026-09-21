import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.user.auth_routes import router as auth_router
from app.presentation.user.profile_routes import router as profile_router
from app.presentation.user.technical_profile_routes import router as technical_profile_router


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
    return app


app = create_app()
