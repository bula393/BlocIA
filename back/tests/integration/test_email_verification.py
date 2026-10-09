from concurrent.futures import ThreadPoolExecutor
import re

import pytest

from app.application.user.verify_email import EmailVerificationError, VerifyEmail
from app.infrastructure.database import Database
from app.infrastructure.user.email_verification_repository import EmailVerificationRepository
from app.infrastructure.user.postgres_repositories import STORE
from app.infrastructure.user.sqlite_repositories import UserRepository
from app.domain.user.user import User


def headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_http_requires_code_before_saving_and_verification_survives_restart(client, access_token, email_verifier):
    auth = headers(access_token)
    verifier, sender, clock = email_verifier
    initial = client.get("/technical-profile/email-verification", headers=auth)
    assert initial.json() == {"verified": False, "email": "usuario.demo@example.com", "expiresInSeconds": None, "resendInSeconds": 0}
    payload = {"providerId": "groq", "token": "private-provider-key"}
    assert client.post("/technical-profile/tokens", headers=auth, json=payload).status_code == 403
    assert not STORE.token_secrets
    sent = client.post("/technical-profile/email-verification/request", headers=auth)
    assert sent.status_code == 200
    mail, code, ttl = sender.messages[-1]
    assert re.fullmatch(r"[0-9]{6}", code) and ttl == 600
    assert code not in sent.text
    record = verifier.repository.get(mail)
    assert record.code_digest != code
    assert client.post("/technical-profile/email-verification/confirm", headers=auth, json={"code": code}).json()["verified"] is True
    assert client.post("/technical-profile/tokens", headers=auth, json=payload).status_code == 200
    reopened = VerifyEmail(EmailVerificationRepository(Database(verifier.repository.database.path)), sender, verifier.secret, lambda: clock[0])
    assert reopened.status(mail)["verified"] is True
    assert reopened.repository.get(mail).code_digest is None
    assert reopened.repository.get(mail).nonce is None


def test_expired_and_replaced_codes_cannot_verify_account(email_verifier, seeded_user, monkeypatch):
    values = iter((123456, 654321))
    monkeypatch.setattr("app.application.user.verify_email.secrets.randbelow", lambda limit: next(values))
    verifier, sender, clock = email_verifier
    verifier.request(seeded_user.mail)
    first = sender.messages[-1][1]
    clock[0] += 601
    with pytest.raises(EmailVerificationError, match="venció"):
        verifier.confirm(seeded_user.mail, first)
    verifier.request(seeded_user.mail)
    second = sender.messages[-1][1]
    with pytest.raises(EmailVerificationError, match="no coincide"):
        verifier.confirm(seeded_user.mail, first)
    assert verifier.confirm(seeded_user.mail, second)["verified"]


def test_guesses_are_persistently_limited_and_correct_code_cannot_bypass_lock(email_verifier, seeded_user):
    verifier, sender, _ = email_verifier
    mail = seeded_user.mail
    verifier.request(mail)
    code = sender.messages[-1][1]
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        with pytest.raises(EmailVerificationError):
            verifier.confirm(mail, wrong)
    assert verifier.repository.get(mail).attempts_left == 0
    with pytest.raises(EmailVerificationError, match="venció"):
        verifier.confirm(mail, code)
    with pytest.raises(EmailVerificationError) as error:
        verifier.require_verified(mail)
    assert error.value.status_code == 403


def test_resend_cooldown_daily_limit_and_concurrent_requests(email_verifier, seeded_user):
    verifier, sender, clock = email_verifier
    mail = seeded_user.mail

    def request(_):
        try:
            verifier.request(mail)
            return "sent"
        except EmailVerificationError as error:
            return error.status_code

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(request, range(5)))
    assert results.count("sent") == 1 and results.count(429) == 4
    assert len(sender.messages) == 1
    for _ in range(9):
        clock[0] += 60
        verifier.request(mail)
    clock[0] += 60
    with pytest.raises(EmailVerificationError) as error:
        verifier.request(mail)
    assert error.value.status_code == 429
    clock[0] += 86400
    verifier.request(mail)
    assert len(sender.messages) == 11


def test_code_is_bound_to_account_and_sender_failure_does_not_verify(email_verifier, seeded_user):
    verifier, sender, clock = email_verifier
    other = User(mail="other@example.com", age=22, profession="Docente")
    UserRepository(verifier.repository.database).save(other)
    verifier.request(seeded_user.mail)
    code = sender.messages[-1][1]
    with pytest.raises(EmailVerificationError):
        verifier.confirm(other.mail, code)
    clock[0] += 60

    class BrokenSender:
        def send_verification(self, *args):
            raise EmailVerificationError("No pudimos enviar el código.", 503)

    verifier.sender = BrokenSender()
    with pytest.raises(EmailVerificationError):
        verifier.request(seeded_user.mail)
    assert verifier.repository.get(seeded_user.mail).send_count == 2
    assert not verifier.status(seeded_user.mail)["verified"]
    with pytest.raises(EmailVerificationError) as error:
        verifier.request(seeded_user.mail)
    assert error.value.status_code == 429
    assert verifier.confirm(seeded_user.mail, code)["verified"]


def test_routes_require_auth_and_return_retry_after(client, access_token, email_verifier):
    for path in ("/technical-profile/email-verification/request", "/technical-profile/email-verification/confirm"):
        assert client.post(path, json={"code": "123456"}).status_code == 401
    assert client.get("/technical-profile/email-verification").status_code == 401
    auth = headers(access_token)
    assert client.post("/technical-profile/email-verification/request", headers=auth).status_code == 200
    denied = client.post("/technical-profile/email-verification/request", headers=auth)
    assert denied.status_code == 429 and denied.headers["Retry-After"] == "60"
    assert client.post("/technical-profile/email-verification/confirm", headers=auth, json={"code": "123"}).status_code == 422
