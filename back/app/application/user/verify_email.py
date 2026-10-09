"""Prove ownership of the account email before storing personal API credentials."""

from dataclasses import dataclass
import hashlib
import hmac
import math
import secrets
import time


class EmailVerificationError(Exception):
    def __init__(self, message: str, status_code: int = 400, retry_after: int | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


@dataclass
class EmailVerification:
    verified_at: float | None = None
    code_digest: str | None = None
    nonce: str | None = None
    expires_at: float = 0
    attempts_left: int = 0
    sent_at: float = 0
    window_started_at: float = 0
    send_count: int = 0


class VerifyEmail:
    CODE_SECONDS = 600
    RESEND_SECONDS = 60
    WINDOW_SECONDS = 86400
    MAX_SENDS = 10
    MAX_ATTEMPTS = 5

    def __init__(self, repository, sender, secret: str, clock=time.time):
        self.repository = repository
        self.sender = sender
        self.secret = secret
        self.clock = clock

    def _status(self, mail, record):
        now = self.clock()
        pending = record and record.code_digest and record.attempts_left > 0 and record.expires_at > now
        return {
            "verified": bool(record and record.verified_at is not None),
            "email": mail,
            "expiresInSeconds": math.ceil(record.expires_at - now) if pending else None,
            "resendInSeconds": max(0, math.ceil(record.sent_at + self.RESEND_SECONDS - now)) if record and record.send_count else 0,
        }

    def status(self, mail):
        return self._status(mail, self.repository.get(mail))

    def require_verified(self, mail):
        if not self.status(mail)["verified"]:
            raise EmailVerificationError("Verificá tu correo antes de guardar una clave propia.", 403)

    def _digest(self, mail, nonce, code):
        if len(self.secret) < 32:
            raise EmailVerificationError("El envío de códigos todavía no está configurado.", 503)
        return hmac.new(self.secret.encode(), f"email-verification\0{mail}\0{nonce}\0{code}".encode(), hashlib.sha256).hexdigest()

    def request(self, mail):
        delivery_error = None
        with self.repository.lock(mail):
            record = self.repository.get(mail) or EmailVerification()
            if record.verified_at is not None:
                return self._status(mail, record)
            now = self.clock()
            remaining = record.sent_at + self.RESEND_SECONDS - now
            if record.send_count and remaining > 0:
                raise EmailVerificationError("Esperá un minuto antes de pedir otro código.", 429, math.ceil(remaining))
            if now >= record.window_started_at + self.WINDOW_SECONDS:
                record.window_started_at, record.send_count = now, 0
            if record.send_count >= self.MAX_SENDS:
                raise EmailVerificationError("Alcanzaste el límite de códigos. Probá de nuevo mañana.", 429,
                                             math.ceil(record.window_started_at + self.WINDOW_SECONDS - now))
            code = f"{secrets.randbelow(1000000):06d}"
            nonce = secrets.token_hex(16)
            digest = self._digest(mail, nonce, code)
            # Failed delivery attempts consume the same limits, preventing SMTP retry floods.
            # Keep the previous challenge if delivery fails. No code is logged or returned.
            try:
                self.sender.send_verification(mail, code, self.CODE_SECONDS)
            except EmailVerificationError as exc:
                delivery_error = exc
            if delivery_error is None:
                record.code_digest, record.nonce = digest, nonce
                record.expires_at = now + self.CODE_SECONDS
                record.attempts_left = self.MAX_ATTEMPTS
            record.sent_at = now
            record.send_count += 1
            self.repository.save(mail, record)
            status = self._status(mail, record)
        if delivery_error:
            raise delivery_error
        return status

    def confirm(self, mail, code):
        error = None
        with self.repository.lock(mail):
            record = self.repository.get(mail)
            if record and record.verified_at is not None:
                return self._status(mail, record)
            if not record or not record.code_digest or record.expires_at <= self.clock() or record.attempts_left <= 0:
                raise EmailVerificationError("El código venció o ya no está disponible. Pedí uno nuevo.")
            expected = self._digest(mail, record.nonce, code)
            if not hmac.compare_digest(record.code_digest, expected):
                record.attempts_left -= 1
                error = EmailVerificationError("El código no coincide. Revisá el correo e intentá de nuevo." if record.attempts_left else
                                               "Alcanzaste el límite de intentos. Pedí un código nuevo.")
            else:
                record.verified_at = self.clock()
                record.code_digest, record.nonce = None, None
                record.expires_at, record.attempts_left = 0, 0
            self.repository.save(mail, record)
            status = self._status(mail, record)
        # Failed guesses must commit too, otherwise a rollback permits unlimited guessing.
        if error:
            raise error
        return status
