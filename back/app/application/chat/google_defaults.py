"""Server-owned Google AI access used when a user has no personal Google key."""

import os

from .settings import ROOT

DEFAULT_GOOGLE_MODEL_ID = "gemini-3.8-flash"


def default_google_key() -> str | None:
    key = os.getenv("BLOCIA_FREE_GOOGLE_KEY", "").strip()
    if key:
        return key
    path = ROOT / "data" / ".free-google.token"
    cipher_path = ROOT / "data" / ".free-google.key"
    if not path.is_file() or not cipher_path.is_file():
        return None
    from cryptography.fernet import Fernet, InvalidToken
    try:
        return Fernet(cipher_path.read_bytes()).decrypt(path.read_bytes()).decode().strip() or None
    except (InvalidToken, ValueError, OSError, UnicodeError):
        return None


def default_google_models() -> list[dict[str, str]]:
    if not default_google_key():
        return []
    return [{
        "providerId": "google",
        "providerName": "Google · predeterminado",
        "modelId": DEFAULT_GOOGLE_MODEL_ID,
        "displayName": "Gemini 3.8 Flash",
    }]


def save_default_google_key(key: str) -> None:
    from cryptography.fernet import Fernet
    directory = ROOT / "data"
    directory.mkdir(parents=True, exist_ok=True)
    cipher_path = directory / ".free-google.key"
    try:
        descriptor = os.open(cipher_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "wb") as file:
            file.write(Fernet.generate_key())
    ciphertext = Fernet(cipher_path.read_bytes()).encrypt(key.strip().encode())
    token_path = directory / ".free-google.token"
    with os.fdopen(os.open(token_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "wb") as file:
        file.write(ciphertext)


if __name__ == "__main__":
    from getpass import getpass

    from app.application.user.list_available_models import GoogleModelsClient

    key = getpass("Clave API de Google AI Studio (entrada oculta): ").strip()
    if not key:
        raise SystemExit("No se guardó ninguna clave.")
    try:
        models = GoogleModelsClient().list_models(key)
    except Exception:
        raise SystemExit("No se pudo validar el catálogo de Google. No se guardó la clave.") from None
    if DEFAULT_GOOGLE_MODEL_ID not in {model.model_id for model in models}:
        raise SystemExit(f"La clave no tiene acceso a {DEFAULT_GOOGLE_MODEL_ID}. No se guardó.")
    save_default_google_key(key)
    print("Clave cifrada guardada. Gemini 3.8 Flash quedó habilitado como respaldo.")
