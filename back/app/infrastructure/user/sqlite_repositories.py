from dataclasses import asdict
from datetime import datetime
from enum import Enum
import json
from typing import get_args, get_type_hints

from app.domain.user.ai_model import AIModel
from app.domain.user.ai_provider import AIProvider
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.password_credential import PasswordCredential
from app.domain.user.provider_token import ProviderToken
from app.domain.user.usage_event import UsageEvent
from app.domain.user.user import User


def serialize(item):
    return json.dumps(asdict(item), ensure_ascii=False, default=lambda value: value.isoformat() if isinstance(value, datetime) else value.value)


def hydrate(cls, payload):
    data = json.loads(payload)
    for field, annotation in get_type_hints(cls).items():
        value = data.get(field)
        if value is None:
            continue
        for kind in get_args(annotation) or (annotation,):
            if kind is datetime:
                data[field] = datetime.fromisoformat(value)
            elif isinstance(kind, type) and issubclass(kind, Enum):
                data[field] = kind(value)
    return cls(**data)


class Repository:
    def __init__(self, database):
        self.database = database

    def transaction(self):
        return self.database.transaction()

    def _get(self, table, cls, where, parameters):
        rows = self.database.query(f"SELECT payload FROM {table} WHERE {where}", parameters)
        return hydrate(cls, rows[0]["payload"]) if rows else None

    def _list(self, table, cls, where="1=1", parameters=()):
        return [hydrate(cls, row["payload"]) for row in self.database.query(f"SELECT payload FROM {table} WHERE {where}", parameters)]

    def _save(self, table, keys, values, item):
        columns = ",".join([*keys, "payload"])
        placeholders = ",".join("?" for _ in range(len(keys) + 1))
        conflict_columns = {
            "users": ("mail",),
            "credentials": ("user_mail",),
            "external_links": ("provider", "external_subject"),
            "providers": ("provider_id",),
            "models": ("provider_id", "model_id"),
            "provider_tokens": ("user_mail", "provider_id"),
        }[table]
        target = ",".join(conflict_columns)
        self.database.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT ({target}) DO UPDATE SET payload=excluded.payload", (*values, serialize(item)))
        return item


class UserRepository(Repository):
    def get(self, mail):
        return self._get("users", User, "mail=?", (mail,))

    def exists(self, mail):
        return self.get(mail) is not None

    def save(self, user):
        user.validate()
        return self._save("users", ["mail"], [user.mail], user)

    def create(self, user):
        user.validate()
        return self.database.execute(
            "INSERT INTO users(mail,payload) VALUES (?,?) ON CONFLICT(mail) DO NOTHING",
            (user.mail, serialize(user)),
        ) == 1

    def revoke_sessions(self, mail, expected_version):
        with self.database.transaction():
            if self.database.is_postgres:
                self.database.query("SELECT mail FROM users WHERE mail=? FOR UPDATE", (mail,))
            user = self.get(mail)
            if user is None or user.auth_version != expected_version:
                return False
            user.auth_version += 1
            self.save(user)
            return True


class CredentialRepository(Repository):
    def get(self, user_mail):
        return self._get("credentials", PasswordCredential, "user_mail=?", (user_mail,))

    def save(self, item):
        return self._save("credentials", ["user_mail"], [item.user_mail], item)

    def delete(self, user_mail):
        return self.database.execute("DELETE FROM credentials WHERE user_mail=?", (user_mail,)) > 0


class ExternalLinkRepository(Repository):
    def get_by_subject(self, provider, external_subject):
        return self._get("external_links", ExternalLoginLink, "provider=? AND external_subject=?", (provider, external_subject))

    def save(self, item):
        return self._save("external_links", ["provider", "external_subject", "user_mail"], [item.provider, item.external_subject, item.user_mail], item)

    def create(self, item):
        return self.database.execute(
            "INSERT INTO external_links(provider,external_subject,user_mail,payload) VALUES (?,?,?,?) "
            "ON CONFLICT(provider,external_subject) DO NOTHING",
            (item.provider, item.external_subject, item.user_mail, serialize(item)),
        ) == 1


class ProviderRepository(Repository):
    def list(self):
        return self._list("providers", AIProvider)

    def get(self, provider_id):
        return self._get("providers", AIProvider, "provider_id=?", (provider_id,))

    def save(self, item):
        return self._save("providers", ["provider_id"], [item.provider_id], item)


class ModelRepository(Repository):
    def list_by_provider(self, provider_id):
        return self._list("models", AIModel, "provider_id=?", (provider_id,))

    def save(self, item):
        return self._save("models", ["provider_id", "model_id"], [item.provider_id, item.model_id], item)


class TokenRepository(Repository):
    def get(self, user_mail, provider_id):
        return self._get("provider_tokens", ProviderToken, "user_mail=? AND provider_id=?", (user_mail, provider_id))

    def save(self, item):
        return self._save("provider_tokens", ["user_mail", "provider_id"], [item.user_mail, item.provider_id], item)

    def _cipher(self):
        from .credential_cipher import credential_cipher
        return credential_cipher(self.database)

    def save_secret(self, user_mail, provider_id, raw_token):
        encrypted = self._cipher().encrypt(raw_token.encode())
        self.database.execute("INSERT INTO token_secrets(user_mail,provider_id,ciphertext) VALUES (?,?,?) ON CONFLICT(user_mail,provider_id) DO UPDATE SET ciphertext=excluded.ciphertext", (user_mail, provider_id, encrypted))

    def get_secret(self, user_mail, provider_id):
        rows = self.database.query("SELECT ciphertext FROM token_secrets WHERE user_mail=? AND provider_id=?", (user_mail, provider_id))
        return self._cipher().decrypt(rows[0]["ciphertext"]).decode() if rows else None

    def delete(self, user_mail, provider_id):
        return bool(self.database.execute("DELETE FROM provider_tokens WHERE user_mail=? AND provider_id=?", (user_mail, provider_id)))

    def list_for_user(self, user_mail):
        return self._list("provider_tokens", ProviderToken, "user_mail=?", (user_mail,))


class UsageRepository(Repository):
    def record(self, item):
        self.database.execute("INSERT INTO usage_events(user_mail,payload) VALUES (?,?)", (item.user_mail, serialize(item)))
        return item

    def list_for_user(self, user_mail):
        return self._list("usage_events", UsageEvent, "user_mail=?", (user_mail,))
