"""Validated HTTP contracts for chat commands."""

import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.application.user.list_available_models import is_free_openrouter_model_id


class SendMessage(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    requestId: UUID
    providerId: str | None = None
    modelId: str | None = None
    acceptPersonalResponse: bool = Field(default=False, strict=True)

    @model_validator(mode="after")
    def model_selection(self):
        if bool(self.providerId) != bool(self.modelId):
            raise ValueError("Elegí un proveedor y un modelo para generar respuestas.")
        if self.modelId and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}", self.modelId):
            raise ValueError("El identificador del modelo no es válido.")
        if self.providerId == "openrouter" and self.modelId and not is_free_openrouter_model_id(self.modelId):
            raise ValueError("Elegí una ruta gratuita de OpenRouter.")
        return self

    @field_validator("prompt")
    @classmethod
    def trim_prompt(cls, value):
        if not value.strip():
            raise ValueError("Escribí una consulta antes de enviarla.")
        return value.strip()
