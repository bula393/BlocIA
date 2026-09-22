"""Exercise the installed database and roll back every verification record."""
import json
from uuid import uuid4

from app.application.user.register_user import RegisterUser
from app.application.user.update_profile import UpdateProfile
from app.application.user.save_provider_token import SaveProviderToken
from app.infrastructure.database import Database, get_database
from app.infrastructure.chat_repository import ChatRepository
from app.infrastructure.user.sqlite_repositories import UserRepository, CredentialRepository, ProviderRepository, TokenRepository


class VerificationRollback(Exception):
    pass


def main():
    database = get_database()
    before = len(database.query("SELECT mail FROM users"))
    assert database.health()["ok"]
    mail = f"verification.{uuid4().hex}@example.com"
    checks = {}
    try:
        with database.transaction():
            users, credentials, tokens = UserRepository(database), CredentialRepository(database), TokenRepository(database)
            RegisterUser(users, credentials).execute(mail, "Verification-9831!", 25, "Estudiante")
            checks["registration_and_password"] = credentials.get(mail).verify("Verification-9831!")
            UpdateProfile(users).execute(mail, age=30, profession="Docente")
            checks["profile_update"] = users.get(mail).profession == "Docente"
            secret = "verification-only-private-token"
            SaveProviderToken(ProviderRepository(database), tokens).execute(mail, "openai", secret)
            checks["encrypted_token_roundtrip"] = tokens.get_secret(mail, "openai") == secret
            ciphertext = database.query("SELECT ciphertext FROM token_secrets WHERE user_mail=?", (mail,))[0][0]
            checks["token_not_plaintext"] = secret.encode() not in ciphertext
            chats = ChatRepository(database)
            conversation = chats.create(mail)
            request_id = str(uuid4())
            chats.reserve(mail, conversation["id"], request_id, "Verificación temporal")
            chats.complete(mail, conversation["id"], request_id, "Verificación temporal", "Respuesta temporal", {"label": "no_personal", "confidence": 1.0})
            checks["conversation_roundtrip"] = len(chats.messages(mail, conversation["id"])) == 2
            checks["idempotency"] = chats.reserve(mail, conversation["id"], request_id, "Verificación temporal") is False
            raise VerificationRollback()
    except VerificationRollback:
        pass
    checks["rollback_removed_verification_data"] = not UserRepository(database).exists(mail) and len(database.query("SELECT mail FROM users")) == before
    restored = Database(database.path)
    checks["reopen_integrity"] = restored.health()["ok"]
    checks["foreign_keys_enabled"] = bool(restored.query("PRAGMA foreign_keys")[0][0])
    checks["wal_enabled"] = restored.query("PRAGMA journal_mode")[0][0] == "wal"
    result = {"passed": all(checks.values()), "checks": checks, "database": restored.health()}
    report = database.path.parent / "database-verification.json"
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
