"""SQLite for local development and PostgreSQL for deployed instances."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
import os
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]


class DatabaseRow:
    """Small row adapter that keeps SQLite's name and positional access on PostgreSQL."""

    def __init__(self, columns, values):
        self._values = tuple(values)
        self._mapping = dict(zip(columns, self._values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._mapping[key]


class Database:
    def __init__(self, path: Path | str | None = None, legacy_path: Path | None = None,
                 database_url: str | None = None):
        # A URL can be passed as the first argument for convenient integrations.
        if database_url is None and isinstance(path, str) and path.startswith(("postgres://", "postgresql://")):
            database_url, path = path, None
        self.database_url = database_url
        self.is_postgres = bool(database_url)
        self._active = ContextVar(f"connection_{id(self)}", default=None)

        if self.is_postgres:
            if os.getenv("ENVIRONMENT", "development").strip().lower() == "production" and not os.getenv("BLOCIA_ENCRYPTION_KEY", "").strip():
                raise ValueError("BLOCIA_ENCRYPTION_KEY es obligatoria en producción cuando se usa PostgreSQL.")
            self.path = None
            self._initialize_postgres()
        else:
            self.path = Path(path or os.getenv("BLOCIA_DATABASE_PATH", str(ROOT / "data/blocia.sqlite3")))
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize_sqlite()
        self._seed_and_import(legacy_path)
        self._migrate_application_data()

    def _migrate_application_data(self):
        """Keep quota records and active work independent of deletable conversations."""
        from app.domain.user.enums import LoginProviderStatus
        from app.infrastructure.user.sqlite_repositories import CredentialRepository, UserRepository

        users, credentials = UserRepository(self), CredentialRepository(self)
        with self.transaction():
            self.execute(
                "UPDATE chat_turns SET lease_id='legacy:'||conversation_id||':'||request_id "
                "WHERE state='pending' AND lease_id IS NULL"
            )
            pending = self.query(
                "SELECT conversations.user_mail,turns.conversation_id,turns.request_id,turns.lease_id,turns.started_at "
                "FROM chat_turns AS turns JOIN conversations ON conversations.id=turns.conversation_id "
                "WHERE turns.state='pending' ORDER BY turns.started_at"
            )
            for row in pending:
                self.execute(
                    "INSERT INTO active_chat_work(user_mail,conversation_id,request_id,lease_id,started_at) "
                    "VALUES (?,?,?,?,?) ON CONFLICT(user_mail) DO NOTHING",
                    (row["user_mail"], row["conversation_id"], row["request_id"], row["lease_id"], row["started_at"]),
                )
            if not self.query("SELECT 1 FROM app_meta WHERE key='quota_ledger_v2'"):
                label = ("(question.classification::jsonb ->> 'label')" if self.is_postgres
                         else "json_extract(question.classification,'$.label')")
                self.execute(
                    "INSERT INTO quota_usage(user_mail,conversation_id,request_id,completed_at,duration_seconds,personal_question) "
                    f"SELECT conversations.user_mail,turns.conversation_id,turns.request_id,turns.completed_at,turns.duration_seconds,({label} IN ('personal_informativa','personal_decision')) "
                    "FROM chat_turns AS turns JOIN conversations ON conversations.id=turns.conversation_id "
                    "JOIN messages AS question ON question.conversation_id=turns.conversation_id "
                    "AND question.request_id=turns.request_id AND question.role='user' "
                    "WHERE turns.state='completed' AND turns.completed_at IS NOT NULL "
                    "ON CONFLICT(user_mail,conversation_id,request_id) DO NOTHING"
                )
                self.execute("INSERT INTO app_meta(key,value) VALUES ('quota_ledger_v2','complete')")

            # Earlier Google linking retained the password credential. Retire
            # that login path and invalidate sessions issued before recovery.
            if not self.query("SELECT 1 FROM app_meta WHERE key='google_password_retirement_v1'"):
                for row in self.query("SELECT user_mail FROM external_links WHERE provider='google'"):
                    user = users.get(row["user_mail"])
                    if user is None:
                        continue
                    credential = credentials.get(user.mail)
                    if (user.password_status or credential is not None
                            or user.login_provider_status == LoginProviderStatus.PASSWORD_AND_GOOGLE):
                        user.password_status = False
                        user.login_provider_status = LoginProviderStatus.GOOGLE
                        user.auth_version += 1
                        users.save(user)
                        credentials.delete(user.mail)
                self.execute("INSERT INTO app_meta(key,value) VALUES ('google_password_retirement_v1','complete')")

            if not self.query("SELECT 1 FROM app_meta WHERE key='registration_total_counter_v1'"):
                existing_accounts = int(self.query("SELECT COUNT(*) AS total FROM users")[0]["total"] or 0)
                self.execute(
                    "INSERT INTO abuse_counters(scope,subject,window_started_at,hit_count) VALUES ('registration-total','global',0,?) "
                    "ON CONFLICT(scope,subject,window_started_at) DO NOTHING",
                    (existing_accounts,),
                )
                self.execute("INSERT INTO app_meta(key,value) VALUES ('registration_total_counter_v1','complete')")

    def connect(self):
        if self.is_postgres:
            import psycopg
            from psycopg.rows import tuple_row
            return psycopg.connect(self.database_url, autocommit=True, connect_timeout=10, row_factory=tuple_row)
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def _execute(self, connection, sql, parameters=()):
        if self.is_postgres:
            # Application SQL uses SQLite-style qmark parameters in both local and
            # production modes. Escape SQL percent wildcards for psycopg before
            # converting parameter markers.
            sql = sql.replace("%", "%%").replace("?", "%s")
        return connection.execute(sql, parameters)

    def _initialize_sqlite(self):
        connection = self.connect()
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript((Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))
            message_columns = {row["name"] for row in connection.execute("PRAGMA table_info(messages)")}
            if "provider_id" not in message_columns:
                connection.execute("ALTER TABLE messages ADD COLUMN provider_id TEXT")
            if "model_id" not in message_columns:
                connection.execute("ALTER TABLE messages ADD COLUMN model_id TEXT")
            turn_columns = {row["name"] for row in connection.execute("PRAGMA table_info(chat_turns)")}
            if "phase" not in turn_columns:
                connection.execute("ALTER TABLE chat_turns ADD COLUMN phase TEXT NOT NULL DEFAULT 'classifying'")
            if "completed_at" not in turn_columns:
                connection.execute("ALTER TABLE chat_turns ADD COLUMN completed_at REAL")
            if "duration_seconds" not in turn_columns:
                connection.execute("ALTER TABLE chat_turns ADD COLUMN duration_seconds REAL NOT NULL DEFAULT 0")
            if "lease_id" not in turn_columns:
                connection.execute("ALTER TABLE chat_turns ADD COLUMN lease_id TEXT")
            connection.execute(
                "UPDATE chat_turns SET completed_at=COALESCE((SELECT CAST(strftime('%s',messages.created_at) AS REAL) "
                "FROM messages WHERE messages.conversation_id=chat_turns.conversation_id AND messages.request_id=chat_turns.request_id "
                "AND messages.role='assistant' LIMIT 1),started_at), "
                "duration_seconds=MAX(0,COALESCE((SELECT CAST(strftime('%s',messages.created_at) AS REAL) "
                "FROM messages WHERE messages.conversation_id=chat_turns.conversation_id AND messages.request_id=chat_turns.request_id "
                "AND messages.role='assistant' LIMIT 1),started_at)-started_at) "
                "WHERE state='completed' AND completed_at IS NULL"
            )
            connection.execute("CREATE INDEX IF NOT EXISTS turns_completed_at ON chat_turns(completed_at)")
        finally:
            connection.close()

    def _initialize_postgres(self):
        connection = self.connect()
        try:
            schema = (Path(__file__).parent / "schema.postgresql.sql").read_text(encoding="utf-8")
            with connection.transaction():
                for statement in schema.split(";"):
                    if statement.strip():
                        connection.execute(statement)
                connection.execute("ALTER TABLE chat_turns ADD COLUMN IF NOT EXISTS lease_id TEXT")
        finally:
            connection.close()

    @contextmanager
    def transaction(self):
        active = self._active.get()
        if active is not None:
            yield active
            return
        connection = self.connect()
        token = self._active.set(connection)
        try:
            if self.is_postgres:
                with connection.transaction():
                    yield connection
            else:
                connection.execute("BEGIN IMMEDIATE")
                try:
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
        connection = active or self.connect()
        try:
            cursor = self._execute(connection, sql, parameters)
            rows = cursor.fetchall()
            if not self.is_postgres:
                return rows
            columns = [column.name for column in cursor.description]
            return [DatabaseRow(columns, row) for row in rows]
        finally:
            if active is None:
                connection.close()

    def execute(self, sql, parameters=()):
        with self.transaction() as connection:
            return self._execute(connection, sql, parameters).rowcount

    def is_integrity_error(self, error):
        if self.is_postgres:
            import psycopg
            return isinstance(error, psycopg.IntegrityError)
        return isinstance(error, sqlite3.IntegrityError)

    def _seed_and_import(self, legacy_path):
        from app.infrastructure.user.postgres_repositories import InMemoryUserStore, PersistentUserStore
        from app.infrastructure.user.sqlite_repositories import UserRepository, CredentialRepository, ExternalLinkRepository, ProviderRepository, ModelRepository, TokenRepository, UsageRepository
        defaults = InMemoryUserStore()
        defaults.seed_defaults()
        with self.transaction():
            for provider in defaults.providers.values():
                if ProviderRepository(self).get(provider.provider_id) is None:
                    ProviderRepository(self).save(provider)
            if not self.query("SELECT 1 FROM models LIMIT 1"):
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
        if self.is_postgres:
            try:
                connected = bool(self.query("SELECT 1 AS connected")[0]["connected"])
                return {"ok": connected, "engine": "postgresql"}
            except Exception:
                return {"ok": False, "engine": "postgresql"}
        integrity = [row[0] for row in self.query("PRAGMA integrity_check")]
        foreign_keys = self.query("PRAGMA foreign_key_check")
        return {"ok": integrity == ["ok"] and not foreign_keys, "integrity": integrity, "foreign_key_errors": len(foreign_keys), "engine": "sqlite"}


@lru_cache(maxsize=1)
def get_database():
    legacy_path = Path(os.getenv("BLOCIA_DATA_PATH", str(ROOT / "data/blocia-state.json")))
    return Database(
        os.getenv("BLOCIA_DATABASE_PATH", str(ROOT / "data/blocia.sqlite3")),
        legacy_path,
        database_url=os.getenv("DATABASE_URL"),
    )
