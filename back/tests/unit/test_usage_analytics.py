from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.user.user import User
from app.infrastructure.chat_repository import ChatRepository
from app.infrastructure.database import Database
from app.infrastructure.usage_analytics_repository import (
    DEFAULT_LOCK_DURATION_MINUTES,
    UsageAnalyticsRepository,
    lock_duration_minutes,
)
from app.infrastructure.user.sqlite_repositories import UserRepository


MAIL = "usage@example.com"
NOW = 1_800_000_000


@pytest.fixture
def usage(tmp_path, monkeypatch):
    monkeypatch.delenv("BLOCIA_LOCK_MINUTES", raising=False)
    database = Database(tmp_path / "usage.sqlite3")
    UserRepository(database).save(User(mail=MAIL, age=25, profession="Estudiante"))
    conversation = ChatRepository(database).create(MAIL)
    return UsageAnalyticsRepository(database), conversation["id"]


def complete_turn(usage, completed_at, label="personal_informativa", duration_seconds=1):
    analytics, conversation_id = usage
    repository = ChatRepository(analytics.database)
    request_id = str(uuid4())
    repository.reserve(MAIL, conversation_id, request_id, "Consulta")
    repository.complete(MAIL, conversation_id, request_id, "Consulta", "Respuesta", {"label": label})
    analytics.database.execute(
        "UPDATE chat_turns SET started_at=?,completed_at=?,duration_seconds=? WHERE request_id=?",
        (completed_at - duration_seconds, completed_at, duration_seconds, request_id),
    )


@pytest.mark.parametrize("value", [None, "", "invalid", "0", "-5", "1.5"])
def test_invalid_or_missing_lock_duration_uses_default(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("BLOCIA_LOCK_MINUTES", raising=False)
    else:
        monkeypatch.setenv("BLOCIA_LOCK_MINUTES", value)
    assert lock_duration_minutes() == DEFAULT_LOCK_DURATION_MINUTES


def test_personal_allowance_and_configured_lock_duration(usage, monkeypatch):
    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "15")
    analytics, _ = usage
    assert analytics.current_lock(MAIL, NOW)["personalQuestionsRemaining"] == 3
    for index, label in enumerate(["personal_informativa", "personal_decision", "personal_informativa"]):
        complete_turn(usage, NOW - 3 + index, label)
        lock = analytics.apply_limits(MAIL, NOW)
        assert lock["personalQuestionsRemaining"] == 2 - index
    assert lock["blocked"] is True
    assert lock["reasonCodes"] == ["personal_questions"]
    assert lock["lockDurationMinutes"] == 15
    assert datetime.fromisoformat(lock["lockUntil"]).timestamp() == NOW + 15 * 60


def test_short_expired_lock_refreshes_allowance_and_preserves_activity(usage, monkeypatch):
    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "1")
    analytics, _ = usage
    for index in range(3):
        complete_turn(usage, NOW - 3 + index)
    analytics.apply_limits(MAIL, NOW)
    assert analytics.current_lock(MAIL, NOW + 59)["blocked"] is True

    expired = analytics.current_lock(MAIL, NOW + 60)
    assert expired["blocked"] is False
    assert expired["reasonCodes"] == []
    assert expired["lockUntil"] is None
    assert expired["personalQuestions"] == 0
    assert expired["personalQuestionsRemaining"] == 3
    assert expired["usageSeconds"] == 0
    dashboard = analytics.dashboard(MAIL, now=NOW + 61)
    assert dashboard["summary"]["totalQueries"] == 3
    assert dashboard["summary"]["personalQueries"] == 3
    assert len(dashboard["activity"]["items"]) == 3
    assert len(analytics.database.query("SELECT * FROM user_usage_resets")) == 1

    for index in range(3):
        complete_turn(usage, NOW + 61 + index)
        next_lock = analytics.apply_limits(MAIL, NOW + 61 + index)
        assert next_lock["personalQuestions"] == index + 1
        assert next_lock["blocked"] is (index == 2)
    assert next_lock["personalQuestionsRemaining"] == 0
    assert analytics.current_lock(MAIL, NOW + 123)["personalQuestionsRemaining"] == 3
    assert analytics.dashboard(MAIL, now=NOW + 124)["summary"]["totalQueries"] == 6
    assert len(analytics.database.query("SELECT * FROM user_usage_resets")) == 2


def test_rechecking_limits_keeps_original_expiry_and_combines_reasons(usage, monkeypatch):
    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "5")
    analytics, _ = usage
    for index in range(3):
        complete_turn(usage, NOW - 3 + index)
    initial = analytics.apply_limits(MAIL, NOW)
    repeated = analytics.apply_limits(MAIL, NOW + 10)
    assert repeated["lockUntil"] == initial["lockUntil"]
    complete_turn(usage, NOW + 11, label="no_personal", duration_seconds=10800)
    combined = analytics.apply_limits(MAIL, NOW + 11)
    assert combined["reasonCodes"] == ["usage_time", "personal_questions"]
    assert combined["lockUntil"] == initial["lockUntil"]


def test_active_lock_keeps_original_duration_after_configuration_changes(usage, monkeypatch):
    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "5")
    analytics, _ = usage
    for index in range(3):
        complete_turn(usage, NOW - 3 + index)
    initial = analytics.apply_limits(MAIL, NOW)

    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "2")
    active = analytics.current_lock(MAIL, NOW + 10)
    assert active["lockUntil"] == initial["lockUntil"]
    assert active["lockDurationMinutes"] == 5
    unlocked = analytics.current_lock(MAIL, NOW + 300)
    assert unlocked["blocked"] is False
    assert unlocked["lockDurationMinutes"] == 2

    for index in range(3):
        complete_turn(usage, NOW + 301 + index)
    next_lock = analytics.apply_limits(MAIL, NOW + 303)
    assert next_lock["blocked"] is True
    assert next_lock["lockDurationMinutes"] == 2
    assert datetime.fromisoformat(next_lock["lockUntil"]).timestamp() == NOW + 423


def test_time_limit_uses_configured_lock_and_expiry_resets_effective_usage(usage, monkeypatch):
    monkeypatch.setenv("BLOCIA_LOCK_MINUTES", "2")
    analytics, _ = usage
    complete_turn(usage, NOW, label="no_personal", duration_seconds=10800)
    lock = analytics.apply_limits(MAIL, NOW)
    assert lock["blocked"] is True
    assert lock["reasonCodes"] == ["usage_time"]
    assert lock["usageLimitSeconds"] == 10800
    assert datetime.fromisoformat(lock["lockUntil"]).timestamp() == NOW + 120
    expired = analytics.apply_limits(MAIL, NOW + 120)
    assert expired["blocked"] is False
    assert expired["usageSeconds"] == 0
    assert analytics.dashboard(MAIL, now=NOW + 120)["summary"]["totalQueries"] == 1


def test_unblocked_allowance_still_uses_rolling_24_hour_window(usage):
    analytics, _ = usage
    complete_turn(usage, NOW - 86401)
    complete_turn(usage, NOW - 1)
    lock = analytics.current_lock(MAIL, NOW)
    assert lock["blocked"] is False
    assert lock["personalQuestions"] == 1
    assert lock["personalQuestionsRemaining"] == 2
    assert lock["lockDurationMinutes"] == 1440
