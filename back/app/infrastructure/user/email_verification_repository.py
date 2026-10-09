"""Persistent challenges, shared by all API workers and both database engines."""

from contextlib import contextmanager

from app.application.user.verify_email import EmailVerification, EmailVerificationError


class EmailVerificationRepository:
    FIELDS = ("verified_at", "code_digest", "nonce", "expires_at", "attempts_left", "sent_at", "window_started_at", "send_count")

    def __init__(self, database):
        self.database = database

    @contextmanager
    def lock(self, mail):
        with self.database.transaction():
            suffix = " FOR UPDATE" if self.database.is_postgres else ""
            # Lock the account even before its first verification row exists.
            if not self.database.query("SELECT mail FROM users WHERE mail=?" + suffix, (mail,)):
                raise EmailVerificationError("La cuenta ya no está disponible.", 401)
            yield

    def get(self, mail):
        rows = self.database.query("SELECT " + ",".join(self.FIELDS) + " FROM email_verifications WHERE user_mail=?", (mail,))
        return EmailVerification(**{name: rows[0][name] for name in self.FIELDS}) if rows else None

    def save(self, mail, record):
        self.database.execute(
            "INSERT INTO email_verifications(user_mail," + ",".join(self.FIELDS) + ") VALUES (?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(user_mail) DO UPDATE SET " + ",".join(f"{name}=excluded.{name}" for name in self.FIELDS),
            (mail, *(getattr(record, name) for name in self.FIELDS)),
        )
