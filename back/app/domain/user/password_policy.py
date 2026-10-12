import base64
import hashlib
import hmac
import secrets
import re


class PasswordPolicy:
    HASH_SCHEME = "pbkdf2_sha256"
    HASH_ITERATIONS = 600_000
    HASH_SALT_BYTES = 16

    @staticmethod
    def validate(password: str, mail: str) -> None:
        errors: list[str] = []
        if len(password) < 10:
            errors.append("at least 10 characters")
        if not re.search(r"[A-Za-z]", password):
            errors.append("at least one letter")
        if not re.search(r"\d", password):
            errors.append("at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            errors.append("at least one special character")
        local_part = mail.split("@", 1)[0].lower()
        if local_part and local_part in password.lower():
            errors.append("no obvious reuse of the user's mail")
        if errors:
            raise ValueError("Password must include " + ", ".join(errors))

    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(PasswordPolicy.HASH_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PasswordPolicy.HASH_ITERATIONS
        )
        salt_text = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
        digest_text = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        return f"{PasswordPolicy.HASH_SCHEME}${PasswordPolicy.HASH_ITERATIONS}${salt_text}${digest_text}"

    @staticmethod
    def verify(password: str, password_hash: str) -> bool:
        if not isinstance(password_hash, str):
            return False
        if not password_hash.startswith(f"{PasswordPolicy.HASH_SCHEME}$"):
            # Existing accounts keep working and are upgraded after their next
            # successful login. Compare the legacy digest in constant time.
            legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
            return hmac.compare_digest(legacy, password_hash)
        try:
            scheme, rounds_text, salt_text, digest_text = password_hash.split("$", 3)
            rounds = int(rounds_text)
            if (scheme != PasswordPolicy.HASH_SCHEME or rounds < 100_000
                    or rounds > PasswordPolicy.HASH_ITERATIONS):
                return False
            salt = base64.urlsafe_b64decode(salt_text + "=" * (-len(salt_text) % 4))
            expected = base64.urlsafe_b64decode(digest_text + "=" * (-len(digest_text) % 4))
            if len(salt) < PasswordPolicy.HASH_SALT_BYTES or len(expected) != 32:
                return False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError, UnicodeError):
            return False

    @staticmethod
    def needs_rehash(password_hash: str) -> bool:
        if not isinstance(password_hash, str) or not password_hash.startswith(f"{PasswordPolicy.HASH_SCHEME}$"):
            return True
        try:
            scheme, rounds_text, _, _ = password_hash.split("$", 3)
            return scheme != PasswordPolicy.HASH_SCHEME or int(rounds_text) < PasswordPolicy.HASH_ITERATIONS
        except (ValueError, TypeError):
            return True
