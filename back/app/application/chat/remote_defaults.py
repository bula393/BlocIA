"""Server-owned free remote access; secrets never enter API responses."""

import os
from .settings import ROOT


def default_openrouter_key() -> str | None:
    key = os.getenv("BLOCIA_FREE_OPENROUTER_KEY", "").strip()
    if key:
        return key
    path = ROOT / "data" / ".free-openrouter.token"
    cipher_path = ROOT / "data" / ".free-openrouter.key"
    if not path.is_file() or not cipher_path.is_file():
        return None
    from cryptography.fernet import Fernet, InvalidToken
    try:
        return Fernet(cipher_path.read_bytes()).decrypt(path.read_bytes()).decode().strip() or None
    except (InvalidToken, ValueError, OSError, UnicodeError):
        return None


def remote_free_models() -> list[dict[str, str]]:
    if not default_openrouter_key():
        return []
    return [{
        "providerId": "openrouter",
        "providerName": "OpenRouter · gratis",
        "modelId": "openrouter/free",
        "displayName": "Modelo remoto gratuito automático",
    }]


def save_default_openrouter_key(key: str) -> None:
    from cryptography.fernet import Fernet
    directory = ROOT / "data"
    directory.mkdir(parents=True, exist_ok=True)
    cipher_path = directory / ".free-openrouter.key"
    try:
        descriptor = os.open(cipher_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "wb") as file:
            file.write(Fernet.generate_key())
    ciphertext = Fernet(cipher_path.read_bytes()).encrypt(key.strip().encode())
    token_path = directory / ".free-openrouter.token"
    with os.fdopen(os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "wb") as file:
        file.write(ciphertext)


if __name__ == "__main__":
    from getpass import getpass
    from app.application.chat.ai_responder import AIResponder
    from app.application.user.list_available_models import OpenRouterModelsClient
    key = getpass("Clave gratuita de OpenRouter (entrada oculta): ").strip()
    if not key:
        raise SystemExit("No se guardó ninguna clave.")
    try:
        OpenRouterModelsClient().list_models(key)
        AIResponder().generate("openrouter", "openrouter/free", "Respondé solamente OK.", key)
    except Exception:
        raise SystemExit("No se pudo validar una inferencia gratuita. No se guardó la clave.") from None
    save_default_openrouter_key(key)
    print("Clave cifrada guardada. Modelo remoto gratuito de respaldo habilitado.")
