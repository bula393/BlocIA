from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3

import pytest

from app.application.user.register_user import RegisterUser, DuplicateMailError
from app.application.user.save_provider_token import SaveProviderToken
from app.application.user.update_profile import UpdateProfile
from app.domain.user.user import User
from app.infrastructure.database import Database
from app.infrastructure.user.postgres_repositories import PersistentUserStore, UserRepositoryImpl, PasswordCredentialRepositoryImpl
from app.infrastructure.user.sqlite_repositories import UserRepository, CredentialRepository, TokenRepository, ProviderRepository


def register(database, mail="sqlite@example.com"):
    return RegisterUser(UserRepository(database), CredentialRepository(database)).execute(mail, "ClaveSegura-123", 27, "Estudiante")[0]


def test_accounts_profile_and_encrypted_tokens_survive_reopening(tmp_path):
    path = tmp_path / "state.sqlite3"
    database = Database(path)
    user = register(database)
    UpdateProfile(UserRepository(database)).execute(user.mail, age=29, profession="Docente")
    secret = "sk-local-persistence-private-key-123456"
    SaveProviderToken(ProviderRepository(database), TokenRepository(database)).execute(user.mail, "openai", secret)
    restored = Database(path)
    assert restored.health() == {"ok": True, "integrity": ["ok"], "foreign_key_errors": 0, "engine": "sqlite"}
    assert UserRepository(restored).get(user.mail).profession == "Docente"
    assert UserRepository(restored).get(user.mail).age == 29
    assert CredentialRepository(restored).get(user.mail).verify("ClaveSegura-123")
    assert TokenRepository(restored).get_secret(user.mail, "openai") == secret
    assert secret.encode() not in path.read_bytes()
    assert secret.encode() not in bytes(restored.query("SELECT ciphertext FROM token_secrets")[0][0])
    assert TokenRepository(restored).delete(user.mail, "openai")
    assert TokenRepository(Database(path)).get_secret(user.mail, "openai") is None


def test_registration_rolls_back_both_records_on_failure(tmp_path):
    database = Database(tmp_path / "rollback.sqlite3")

    class BrokenCredentials(CredentialRepository):
        def save(self, item):
            super().save(item)
            raise RuntimeError("Simulated write failure")

    with pytest.raises(RuntimeError):
        RegisterUser(UserRepository(database), BrokenCredentials(database)).execute("rollback@example.com", "ClaveSegura-123", 20, "Estudiante")
    assert not UserRepository(database).exists("rollback@example.com")
    assert not database.query("SELECT 1 FROM credentials")


def test_token_metadata_and_secret_are_atomic(tmp_path, monkeypatch):
    database = Database(tmp_path / "tokens.sqlite3")
    user = register(database)
    tokens = TokenRepository(database)

    def fail(*args):
        raise OSError("Simulated encryption failure")

    monkeypatch.setattr(tokens, "save_secret", fail)
    with pytest.raises(OSError):
        SaveProviderToken(ProviderRepository(database), tokens).execute(user.mail, "openai", "private-token")
    assert tokens.get(user.mail, "openai") is None


def test_invalid_profile_and_foreign_keys_preserve_integrity(tmp_path):
    database = Database(tmp_path / "constraints.sqlite3")
    user = register(database)
    with pytest.raises(ValueError):
        UpdateProfile(UserRepository(database)).execute(user.mail, age=99, profession=" ")
    assert UserRepository(database).get(user.mail).age == 27
    with pytest.raises(sqlite3.IntegrityError):
        database.execute("INSERT INTO credentials(user_mail,payload) VALUES (?,?)", ("orphan@example.com", "{}"))
    with pytest.raises(sqlite3.IntegrityError):
        database.execute("INSERT INTO users(mail,payload) VALUES (?,?)", ("invalid@example.com", json.dumps({"mail": "invalid@example.com", "age": -2, "profession": "Estudiante"})))
    assert database.health()["ok"]


def test_concurrent_registration_and_writes_do_not_lose_data(tmp_path):
    path = tmp_path / "concurrent.sqlite3"
    database = Database(path)

    def create(index):
        try:
            register(database, "same@example.com")
            return "created"
        except DuplicateMailError:
            return "duplicate"

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(create, range(6)))
    assert results.count("created") == 1
    assert results.count("duplicate") == 5
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda i: register(database, f"unique{i}@example.com"), range(10)))
    assert len(Database(path).query("SELECT mail FROM users")) == 11
    assert len(database.query("SELECT user_mail FROM credentials")) == 11
    assert database.health()["ok"]


def test_import_preserves_original_file_and_is_idempotent(tmp_path):
    legacy_path = tmp_path / "old.json"
    legacy = PersistentUserStore(legacy_path)
    user, _ = RegisterUser(UserRepositoryImpl(legacy), PasswordCredentialRepositoryImpl(legacy)).execute("legacy@example.com", "ClaveSegura-123", 28, "Estudiante")
    original = legacy_path.read_bytes()
    path = tmp_path / "new.sqlite3"
    database = Database(path, legacy_path)
    assert UserRepository(database).get(user.mail).age == 28
    assert CredentialRepository(database).get(user.mail).verify("ClaveSegura-123")
    assert legacy_path.read_bytes() == original
    assert len(Database(path, legacy_path).query("SELECT mail FROM users")) == 1


def test_corrupt_legacy_data_is_not_overwritten(tmp_path):
    source = tmp_path / "bad.json"
    source.write_text("{bad json", encoding="utf-8")
    with pytest.raises(RuntimeError):
        Database(tmp_path / "new.sqlite3", source)
    assert source.read_text() == "{bad json"
