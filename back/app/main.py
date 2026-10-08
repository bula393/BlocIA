"""API process entry point; modules are assembled in bootstrap."""

from contextlib import asynccontextmanager

from app.infrastructure.dev_environment import load_dev_environment

load_dev_environment()

from app.application.chat.ai_responder import local_text_model
from app.application.chat.local_models import local_models
from app.bootstrap import application_lifespan, create_application
from app.presentation.chat_routes import ai_responder


@asynccontextmanager
async def lifespan(app):
    async with application_lifespan(local_models, local_text_model, ai_responder):
        yield


def create_app():
    return create_application(lifespan)


app = create_app()
