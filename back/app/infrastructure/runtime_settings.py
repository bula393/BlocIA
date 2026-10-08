"""Environment configuration shared by the API bootstrap and health endpoints."""

from dataclasses import dataclass
import os
from urllib.parse import urlsplit


@dataclass(frozen=True)
class RuntimeSettings:
    production: bool
    frontend_url: str
    release: str

    @classmethod
    def from_environment(cls):
        production = os.getenv("ENVIRONMENT", "development").strip().lower() == "production"
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").strip().rstrip("/")
        if production:
            secret = os.getenv("ACCESS_TOKEN_SECRET", "").strip()
            if len(secret) < 32:
                raise ValueError("ACCESS_TOKEN_SECRET debe tener al menos 32 caracteres en producción.")
            parsed = urlsplit(frontend_url)
            if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                    or parsed.path or parsed.query or parsed.fragment):
                raise ValueError("FRONTEND_URL debe ser el origen HTTPS público, sin rutas, en producción.")
            if os.getenv("BLOCIA_INFERENCE_URL", "").strip() and not os.getenv("BLOCIA_INFERENCE_TOKEN", "").strip():
                raise ValueError("BLOCIA_INFERENCE_TOKEN es obligatorio al separar la IA en producción.")
        return cls(production, frontend_url, os.getenv("RELEASE_TAG", "development").strip() or "development")
