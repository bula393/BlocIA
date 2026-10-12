"""Shared encryption for personal API keys and provider OAuth sessions."""

import os

from cryptography.fernet import Fernet


def credential_cipher(database):
    key = os.getenv("BLOCIA_ENCRYPTION_KEY")
    if key:
        return Fernet(key.encode())
    if database.is_postgres:
        raise RuntimeError("BLOCIA_ENCRYPTION_KEY es obligatoria para cifrar credenciales con PostgreSQL.")
    key_path = database.path.parent / ".token-encryption.key"
    try:
        descriptor = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "wb") as file:
            file.write(Fernet.generate_key())
    return Fernet(key_path.read_bytes())
