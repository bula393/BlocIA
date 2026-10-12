"""Encrypted, user-scoped OAuth storage shared by SQLite and PostgreSQL."""

from contextlib import contextmanager
import hashlib
import hmac
import json
import time

from .credential_cipher import credential_cipher


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class ProviderOAuthRepository:
    def __init__(self, database):
        self.database = database

    def get(self, mail, *, for_update=False):
        suffix = " FOR UPDATE" if for_update and self.database.is_postgres else ""
        rows = self.database.query("SELECT ciphertext FROM provider_oauth_accounts WHERE user_mail=? AND provider_id='google'" + suffix, (mail,))
        return json.loads(credential_cipher(self.database).decrypt(bytes(rows[0]["ciphertext"]))) if rows else None

    def save(self, mail, account):
        encrypted = credential_cipher(self.database).encrypt(json.dumps(account, separators=(",", ":")).encode())
        self.database.execute("INSERT INTO provider_oauth_accounts(user_mail,provider_id,ciphertext) VALUES (?,'google',?) ON CONFLICT(user_mail,provider_id) DO UPDATE SET ciphertext=excluded.ciphertext", (mail, encrypted))

    def delete(self, mail):
        self.database.execute("DELETE FROM provider_oauth_accounts WHERE user_mail=? AND provider_id='google'", (mail,))

    @contextmanager
    def locked(self, mail):
        with self.database.transaction():
            yield self.get(mail, for_update=True)

    def begin(self, mail, state, browser, payload):
        encrypted = credential_cipher(self.database).encrypt(json.dumps(payload).encode())
        with self.database.transaction():
            self.database.execute("DELETE FROM provider_oauth_transactions WHERE expires_at<=? OR user_mail=?", (time.time(), mail))
            self.database.execute("INSERT INTO provider_oauth_transactions(state_hash,user_mail,browser_hash,ciphertext,expires_at) VALUES (?,?,?,?,?)", (digest(state), mail, digest(browser), encrypted, time.time() + 600))

    def consume(self, mail, state, browser):
        if not state or not browser or len(state) > 256 or len(browser) > 256:
            return None
        with self.database.transaction():
            suffix = " FOR UPDATE" if self.database.is_postgres else ""
            rows = self.database.query("SELECT user_mail,browser_hash,ciphertext,expires_at FROM provider_oauth_transactions WHERE state_hash=?" + suffix, (digest(state),))
            if not rows:
                return None
            row = rows[0]
            if row["user_mail"] != mail or row["expires_at"] <= time.time() or not hmac.compare_digest(row["browser_hash"], digest(browser)):
                return None
            self.database.execute("DELETE FROM provider_oauth_transactions WHERE state_hash=?", (digest(state),))
            return json.loads(credential_cipher(self.database).decrypt(bytes(row["ciphertext"])))
