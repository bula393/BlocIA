"""PostgreSQL smoke coverage; CI supplies an isolated Postgres service."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
import time
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet

from app.application.user.register_user import RegisterUser
from app.application.user.save_provider_token import SaveProviderToken
from app.application.user.verify_email import EmailVerificationError, VerifyEmail
from app.infrastructure.chat_repository import ChatRepository
from app.infrastructure.database import Database
from app.infrastructure.usage_analytics_repository import UsageAnalyticsRepository
from app.infrastructure.user.email_verification_repository import EmailVerificationRepository
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


@pytest.fixture
def postgres_email_account(monkeypatch):
    monkeypatch.setenv("BLOCIA_ENCRYPTION_KEY", Fernet.generate_key().decode())
    monkeypatch.setattr("app.application.user.verify_email.secrets.randbelow", lambda limit: 123456)
    database = Database(database_url=POSTGRES_URL, legacy_path=None)
    mail = f"postgres-otp-{uuid4().hex}@example.com"
    RegisterUser(UserRepository(database), CredentialRepository(database)).execute(
        mail, "ClaveSegura-123", 27, "Estudiante"
    )
    try:
        yield database, mail
    finally:
        database.execute("DELETE FROM users WHERE mail=?", (mail,))


class CapturingVerificationSender:
    def __init__(self):
        self.deliveries = []

    def send_verification(self, mail, code, expires_seconds):
        self.deliveries.append((mail, code, expires_seconds))


def test_postgres_email_failed_guesses_commit_and_verified_challenge_is_consumed(postgres_email_account):
    database, mail = postgres_email_account
    sender = CapturingVerificationSender()
    clock = lambda: 1_720_000_000
    verification = VerifyEmail(EmailVerificationRepository(database), sender, "test-email-secret-" * 3, clock)
    assert not verification.request(mail)["verified"]
    assert sender.deliveries == [(mail, "123456", 600)]
    record = EmailVerificationRepository(database).get(mail)
    assert record.code_digest != "123456" and len(record.code_digest) == 64

    with pytest.raises(EmailVerificationError, match="no coincide"):
        verification.confirm(mail, "000000")

    restarted = Database(database_url=POSTGRES_URL, legacy_path=None)
    repository = EmailVerificationRepository(restarted)
    assert repository.get(mail).attempts_left == 4
    verification = VerifyEmail(repository, sender, "test-email-secret-" * 3, clock)
    assert verification.confirm(mail, "123456")["verified"]
    persisted = repository.get(mail)
    assert persisted.verified_at == clock()
    assert persisted.code_digest is None and persisted.nonce is None
    assert persisted.attempts_left == persisted.expires_at == 0
    assert verification.request(mail)["verified"]
    assert len(sender.deliveries) == 1


def test_postgres_first_email_request_locks_account_before_challenge_exists(postgres_email_account):
    from psycopg.conninfo import make_conninfo

    database, mail = postgres_email_account
    application_name = f"otp-contention-{uuid4().hex}"
    second_database = Database(
        database_url=make_conninfo(POSTGRES_URL, application_name=application_name), legacy_path=None
    )
    delivery_entered, release_delivery = Event(), Event()

    class HoldingSender(CapturingVerificationSender):
        def send_verification(self, *args):
            super().send_verification(*args)
            delivery_entered.set()
            assert release_delivery.wait(20), "Test did not release the first delivery"

    first_sender, second_sender = HoldingSender(), CapturingVerificationSender()
    secret, clock = "test-email-secret-" * 3, lambda: 1_720_000_000
    first = VerifyEmail(EmailVerificationRepository(database), first_sender, secret, clock)
    second = VerifyEmail(EmailVerificationRepository(second_database), second_sender, secret, clock)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first_request = pool.submit(first.request, mail)
        try:
            assert delivery_entered.wait(5)
            second_request = pool.submit(second.request, mail)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                rows = database.query(
                    "SELECT wait_event_type FROM pg_stat_activity WHERE application_name=?",
                    (application_name,),
                )
                if any(row["wait_event_type"] == "Lock" for row in rows):
                    break
                time.sleep(0.01)
            else:
                pytest.fail("The concurrent first request did not wait for the account row lock")
        finally:
            release_delivery.set()
        assert not first_request.result(timeout=5)["verified"]
        with pytest.raises(EmailVerificationError) as captured:
            second_request.result(timeout=5)
    assert captured.value.status_code == 429 and captured.value.retry_after == 60
    assert len(first_sender.deliveries) == 1 and not second_sender.deliveries
    assert EmailVerificationRepository(database).get(mail).send_count == 1


def test_postgres_concurrent_email_guesses_cannot_lose_attempt_decrements(postgres_email_account):
    database, mail = postgres_email_account
    verification = VerifyEmail(
        EmailVerificationRepository(database), CapturingVerificationSender(),
        "test-email-secret-" * 3, lambda: 1_720_000_000,
    )
    verification.request(mail)
    ready = Barrier(8)

    def guess():
        ready.wait(timeout=5)
        with pytest.raises(EmailVerificationError) as captured:
            verification.confirm(mail, "000000")
        return str(captured.value)

    with ThreadPoolExecutor(max_workers=8) as pool:
        errors = list(pool.map(lambda _: guess(), range(8)))
    assert sum("no coincide" in message for message in errors) == 4
    assert sum("límite de intentos" in message for message in errors) == 1
    record = EmailVerificationRepository(database).get(mail)
    assert record.attempts_left == 0 and record.verified_at is None
    with pytest.raises(EmailVerificationError, match="venció"):
        verification.confirm(mail, "123456")


def test_postgres_failed_email_delivery_commits_cooldown_and_preserves_previous_challenge(postgres_email_account):
    database, mail = postgres_email_account
    now = [1_720_000_000]
    repository = EmailVerificationRepository(database)
    verification = VerifyEmail(repository, CapturingVerificationSender(), "test-email-secret-" * 3, lambda: now[0])
    verification.request(mail)
    previous = repository.get(mail)
    now[0] += verification.RESEND_SECONDS

    class UnavailableSender:
        calls = 0

        def send_verification(self, *args):
            self.calls += 1
            raise EmailVerificationError("SMTP unavailable", 503)

    unavailable = UnavailableSender()
    verification.sender = unavailable
    with pytest.raises(EmailVerificationError) as captured:
        verification.request(mail)
    assert captured.value.status_code == 503

    restarted = Database(database_url=POSTGRES_URL, legacy_path=None)
    persisted = EmailVerificationRepository(restarted).get(mail)
    assert persisted.send_count == 2 and persisted.sent_at == now[0]
    assert (persisted.code_digest, persisted.nonce, persisted.expires_at, persisted.attempts_left) == (
        previous.code_digest, previous.nonce, previous.expires_at, previous.attempts_left,
    )
    with pytest.raises(EmailVerificationError) as captured:
        verification.request(mail)
    assert captured.value.status_code == 429 and unavailable.calls == 1
    assert verification.confirm(mail, "123456")["verified"]
