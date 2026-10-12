"""Small persistent admission budgets shared across API workers."""

import math
import os
import time


DAY_SECONDS = 24 * 60 * 60
MAX_CONFIGURED_LIMIT = 1_000_000


def configured_limit(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return min(MAX_CONFIGURED_LIMIT, value) if value > 0 else default


class AbuseLimitExceeded(Exception):
    def __init__(self, message: str, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__(message)


class AbuseLimitRepository:
    """Atomically reserve a fixed-window budget in SQLite or PostgreSQL."""

    def __init__(self, database, clock=time.time):
        self.database = database
        self.clock = clock

    def consume(self, scope: str, subject: str, *, limit: int, window_seconds: int | None,
                message: str) -> None:
        if not 1 <= limit <= MAX_CONFIGURED_LIMIT:
            raise ValueError("Rate-limit values must be positive and bounded")
        now = int(self.clock())
        window_start = 0 if window_seconds is None else (now // window_seconds) * window_seconds
        retry_after = None if window_seconds is None else max(1, math.ceil(window_start + window_seconds - now))
        allowed = False
        with self.database.transaction():
            self.database.execute(
                "INSERT INTO abuse_counters(scope,subject,window_started_at,hit_count) VALUES (?,?,?,0) "
                "ON CONFLICT(scope,subject,window_started_at) DO NOTHING",
                (scope, subject, window_start),
            )
            allowed = self.database.execute(
                "UPDATE abuse_counters SET hit_count=hit_count+1 "
                "WHERE scope=? AND subject=? AND window_started_at=? AND hit_count<?",
                (scope, subject, window_start, limit),
            ) == 1
            if window_seconds is not None:
                self.database.execute(
                    "DELETE FROM abuse_counters WHERE scope=? AND window_started_at<?",
                    (scope, window_start - window_seconds * 7),
                )
        if not allowed:
            raise AbuseLimitExceeded(message, retry_after)

    def admit_registration(self) -> None:
        self.consume(
            "registration-daily", "global",
            limit=configured_limit("BLOCIA_REGISTRATION_MAX_PER_DAY", 500),
            window_seconds=DAY_SECONDS,
            message="Se alcanzó el límite diario de registros. Probá de nuevo más tarde.",
        )
        self.consume(
            "registration-total", "global",
            limit=configured_limit("BLOCIA_MAX_ACCOUNTS", 100_000),
            window_seconds=None,
            message="Se alcanzó la capacidad de cuentas configurada. Contactá al administrador.",
        )

    def admit_email_send(self) -> None:
        self.consume(
            "verification-email-daily", "global",
            limit=configured_limit("BLOCIA_VERIFICATION_EMAIL_MAX_PER_DAY", 250),
            window_seconds=DAY_SECONDS,
            message="Se alcanzó el límite diario de envíos de códigos. Probá de nuevo más tarde.",
        )

    def admit_classification(self, mail: str) -> None:
        self.consume(
            "classification-account-daily", mail,
            limit=configured_limit("BLOCIA_CLASSIFICATION_MAX_PER_USER_PER_DAY", 50),
            window_seconds=DAY_SECONDS,
            message="Alcanzaste el límite diario de clasificaciones para esta cuenta.",
        )
        self.consume(
            "classification-daily", "global",
            limit=configured_limit("BLOCIA_CLASSIFICATION_MAX_PER_DAY", 5000),
            window_seconds=DAY_SECONDS,
            message="Se alcanzó el límite diario de clasificaciones del servicio. Probá de nuevo más tarde.",
        )

    def admit_shared_provider_request(self) -> None:
        self.consume(
            "shared-provider-daily", "global",
            limit=configured_limit("BLOCIA_SHARED_PROVIDER_MAX_PER_DAY", 300),
            window_seconds=DAY_SECONDS,
            message="Se alcanzó el límite diario de consultas con la clave compartida del servicio.",
        )


class InMemoryAbuseLimitRepository:
    """Test-only adapter with the same API and fixed-window semantics."""

    def __init__(self, clock=time.time):
        self.clock = clock
        self.counts: dict[tuple[str, str, int], int] = {}

    def consume(self, scope: str, subject: str, *, limit: int, window_seconds: int | None,
                message: str) -> None:
        now = int(self.clock())
        window_start = 0 if window_seconds is None else (now // window_seconds) * window_seconds
        key = (scope, subject, window_start)
        count = self.counts.get(key, 0)
        if count >= limit:
            retry_after = None if window_seconds is None else max(1, math.ceil(window_start + window_seconds - now))
            raise AbuseLimitExceeded(message, retry_after)
        self.counts[key] = count + 1

    def admit_registration(self) -> None:
        self.consume("registration-daily", "global", limit=configured_limit("BLOCIA_REGISTRATION_MAX_PER_DAY", 500),
                     window_seconds=DAY_SECONDS, message="Se alcanzó el límite diario de registros. Probá de nuevo más tarde.")
        self.consume("registration-total", "global", limit=configured_limit("BLOCIA_MAX_ACCOUNTS", 100_000),
                     window_seconds=None, message="Se alcanzó la capacidad de cuentas configurada. Contactá al administrador.")

    def admit_email_send(self) -> None:
        self.consume("verification-email-daily", "global", limit=configured_limit("BLOCIA_VERIFICATION_EMAIL_MAX_PER_DAY", 250),
                     window_seconds=DAY_SECONDS, message="Se alcanzó el límite diario de envíos de códigos. Probá de nuevo más tarde.")

    def admit_classification(self, mail: str) -> None:
        self.consume("classification-account-daily", mail,
                     limit=configured_limit("BLOCIA_CLASSIFICATION_MAX_PER_USER_PER_DAY", 50),
                     window_seconds=DAY_SECONDS, message="Alcanzaste el límite diario de clasificaciones para esta cuenta.")
        self.consume("classification-daily", "global", limit=configured_limit("BLOCIA_CLASSIFICATION_MAX_PER_DAY", 5000),
                     window_seconds=DAY_SECONDS, message="Se alcanzó el límite diario de clasificaciones del servicio. Probá de nuevo más tarde.")

    def admit_shared_provider_request(self) -> None:
        self.consume("shared-provider-daily", "global", limit=configured_limit("BLOCIA_SHARED_PROVIDER_MAX_PER_DAY", 300),
                     window_seconds=DAY_SECONDS, message="Se alcanzó el límite diario de consultas con la clave compartida del servicio.")
