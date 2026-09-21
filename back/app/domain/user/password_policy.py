import hashlib
import re


class PasswordPolicy:
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
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def verify(password: str, password_hash: str) -> bool:
        return PasswordPolicy.hash_password(password) == password_hash
