from concurrent.futures import ThreadPoolExecutor

import pytest

from app.infrastructure.abuse_limits import AbuseLimitExceeded, AbuseLimitRepository
from app.infrastructure.database import Database
from app.domain.user.user import User
from app.infrastructure.user.sqlite_repositories import UserRepository


def test_fixed_window_budget_is_shared_across_database_instances_and_resets(tmp_path):
    now = [1_800_000_000.0]
    path = tmp_path / "limits.sqlite3"
    first = AbuseLimitRepository(Database(path), lambda: now[0])
    second = AbuseLimitRepository(Database(path), lambda: now[0])

    first.consume("test", "global", limit=2, window_seconds=60, message="limited")
    second.consume("test", "global", limit=2, window_seconds=60, message="limited")
    with pytest.raises(AbuseLimitExceeded) as error:
        first.consume("test", "global", limit=2, window_seconds=60, message="limited")
    assert error.value.retry_after == 60 - (int(now[0]) % 60)

    now[0] += 60
    second.consume("test", "global", limit=2, window_seconds=60, message="limited")


def test_concurrent_consumers_cannot_exceed_budget(tmp_path):
    now = [1_800_000_000.0]
    path = tmp_path / "concurrent-limits.sqlite3"
    databases = [Database(path) for _ in range(2)]
    repositories = [AbuseLimitRepository(database, lambda: now[0]) for database in databases]

    def attempt(index):
        try:
            repositories[index % 2].consume("concurrent", "global", limit=5, window_seconds=300, message="limited")
            return True
        except AbuseLimitExceeded:
            return False

    with ThreadPoolExecutor(max_workers=10) as pool:
        allowed = list(pool.map(attempt, range(20)))

    assert sum(allowed) == 5
    assert databases[0].query(
        "SELECT hit_count FROM abuse_counters WHERE scope='concurrent' AND subject='global'"
    )[0]["hit_count"] == 5


def test_upgrade_seeds_lifetime_account_budget_from_existing_accounts(tmp_path):
    path = tmp_path / "existing-accounts.sqlite3"
    database = Database(path)
    UserRepository(database).save(User(mail="existing@example.com", age=30, profession="Docente"))
    database.execute("DELETE FROM abuse_counters WHERE scope='registration-total'")
    database.execute("DELETE FROM app_meta WHERE key='registration_total_counter_v1'")

    upgraded = Database(path)

    row = upgraded.query(
        "SELECT hit_count FROM abuse_counters WHERE scope='registration-total' AND subject='global' AND window_started_at=0"
    )[0]
    assert row["hit_count"] == 1
