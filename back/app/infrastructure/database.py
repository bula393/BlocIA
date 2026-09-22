"""SQLite persistence with transactions, foreign keys and durable WAL writes."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
import os
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]


class Database:
    def __init__(self, path: Path | str, legacy_path: Path | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._active = ContextVar(f"connection_{id(self)}", default=None)
        connection = self.connect()
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript((Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))
        finally:
            connection.close()
        self._seed_and_import(legacy_path)

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    @contextmanager
    def transaction(self):
        active = self._active.get()
        if active is not None:
            yield active
            return
        connection = self.connect()
        token = self._active.set(connection)
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            self._active.reset(token)
            connection.close()

    def query(self, sql, parameters=()):
        active = self._active.get()
        if active is not None:
            return active.execute(sql, parameters).fetchall()
        connection = self.connect()
        try:
            return connection.execute(sql, parameters).fetchall()
        finally:
            connection.close()

    def execute(self, sql, parameters=()):
        with self.transaction() as connection:
            return connection.execute(sql, parameters).rowcount

    def _seed_and_import(self, legacy_path):
        from app.infrastructure.user.postgres_repositories import InMemoryUserStore, PersistentUserStore
        from app.infrastructure.user.sqlite_repositories import UserRepository, CredentialRepository, ExternalLinkRepository, ProviderRepository, ModelRepository, TokenRepository, UsageRepository
        defaults = InMemoryUserStore()
        defaults.seed_defaults()
        with self.transaction():
            if not self.query("SELECT 1 FROM providers LIMIT 1"):
                for provider in defaults.providers.values():
                    ProviderRepository(self).save(provider)
                for models in defaults.models.values():
                    for model in models:
                        ModelRepository(self).save(model)
            if legacy_path is None or self.query("SELECT 1 FROM app_meta WHERE key='legacy_import'"):
                return
            if legacy_path.exists():
                if self.query("SELECT 1 FROM users LIMIT 1"):
                    raise RuntimeError("Importación cancelada: la base destino ya contiene usuarios.")
                legacy = PersistentUserStore(legacy_path, read_only=True)
                for items, repository in [(legacy.users.values(), UserRepository), (legacy.credentials.values(), CredentialRepository), (legacy.external_links.values(), ExternalLinkRepository), (legacy.providers.values(), ProviderRepository)]:
                    for item in items:
                        repository(self).save(item)
                for models in legacy.models.values():
                    for item in models:
                        ModelRepository(self).save(item)
                for item in legacy.tokens.values():
                    from app.domain.user.enums import ProviderTokenStatusValue
                    item.status = ProviderTokenStatusValue.REQUIRES_ATTENTION
                    TokenRepository(self).save(item)
                for item in legacy.usage_events:
                    UsageRepository(self).record(item)
            self.execute("INSERT INTO app_meta(key,value) VALUES ('legacy_import',?)", (str(legacy_path),))

    def health(self):
        integrity = [row[0] for row in self.query("PRAGMA integrity_check")]
        foreign_keys = self.query("PRAGMA foreign_key_check")
        return {"ok": integrity == ["ok"] and not foreign_keys, "integrity": integrity, "foreign_key_errors": len(foreign_keys), "engine": "sqlite"}


@lru_cache(maxsize=1)
def get_database():
    return Database(os.getenv("BLOCIA_DATABASE_PATH", str(ROOT / "data/blocia.sqlite3")), Path(os.getenv("BLOCIA_DATA_PATH", str(ROOT / "data/blocia-state.json"))))
