"""PostgreSQL smoke coverage; CI supplies an isolated Postgres service."""
import os
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet

from app.application.user.register_user import RegisterUser
from app.application.user.save_provider_token import SaveProviderToken
from app.infrastructure.chat_repository import ChatRepository
from app.infrastructure.database import Database
from app.infrastructure.usage_analytics_repository import UsageAnalyticsRepository
from app.infrastructure.user.sqlite_repositories import CredentialRepository, ProviderRepository, TokenRepository, UserRepository


POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not POSTGRES_URL, reason="TEST_POSTGRES_URL is not configured")


def test_postgres_persistence_chat_analytics_and_encrypted_tokens(monkeypatch):
    encryption_key = Fernet.generate_key().decode()
    monkeypatch.setenv("BLOCIA_ENCRYPTION_KEY", encryption_key)
    database = Database(database_url=POSTGRES_URL, legacy_path=None)
    database.execute(
        "TRUNCATE app_meta, usage_events, messages, chat_turns, conversations, user_usage_resets, "
        "user_usage_locks, token_secrets, provider_tokens, models, providers, external_links, "
        "credentials, users RESTART IDENTITY CASCADE"
    )
    database = Database(database_url=POSTGRES_URL, legacy_path=None)

    mail = f"postgres-{uuid4().hex}@example.com"
    user, _ = RegisterUser(UserRepository(database), CredentialRepository(database)).execute(
        mail, "ClaveSegura-123", 27, "Estudiante"
    )
    token = "sk-postgres-persistence-private-token"
    SaveProviderToken(ProviderRepository(database), TokenRepository(database)).execute(user.mail, "openai", token)
    assert TokenRepository(database).get_secret(user.mail, "openai") == token
    assert token.encode() not in bytes(database.query("SELECT ciphertext FROM token_secrets")[0][0])

    chats = ChatRepository(database)
    conversation = chats.create(user.mail)
    request_id = str(uuid4())
    prompt = "¿Qué opciones personales puedo considerar?"
    assert chats.reserve(user.mail, conversation["id"], request_id, prompt)
    chats.complete(
        user.mail,
        conversation["id"],
        request_id,
        prompt,
        "Podés revisar estas alternativas con una persona de confianza.",
        {"label": "personal_informativa", "confidence": 0.91},
    )

    dashboard = UsageAnalyticsRepository(database).dashboard(user.mail)
    assert dashboard["summary"]["totalQueries"] == 1
    assert dashboard["summary"]["personalQueries"] == 1
    assert dashboard["summary"]["categoryCounts"] == {"personal_informativa": 1}
    assert database.health() == {"ok": True, "engine": "postgresql"}
