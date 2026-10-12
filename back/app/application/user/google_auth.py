import base64
import hashlib
import hmac
import json
import os
import time
from contextlib import nullcontext

from app.domain.user.enums import LoginProviderStatus
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.repositories import ExternalLoginLinkRepository, PasswordCredentialRepository, UserRepository
from app.domain.user.user import User
from .session import create_access_token


class GoogleCompletionRequired(Exception):
    def __init__(self, registration_token: str, missing_fields: list[str], prefilled_fields: dict):
        self.registration_token = registration_token
        self.missing_fields = missing_fields
        self.prefilled_fields = prefilled_fields


def registration_token(subject: str, mail: str) -> str:
    """Carry the verified Google identity through the short profile-completion step."""
    payload = json.dumps({"subject": subject, "mail": mail, "exp": int(time.time()) + 600}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).decode()
    signature = hmac.new(google_registration_secret(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"google:{encoded}.{signature}"


def google_registration_secret() -> bytes:
    secret = os.getenv("GOOGLE_REGISTRATION_SECRET", "").strip().encode("utf-8")
    if secret:
        if len(secret) < 32:
            raise RuntimeError("GOOGLE_REGISTRATION_SECRET debe tener al menos 32 caracteres aleatorios.")
        return secret
    access_secret = os.getenv("ACCESS_TOKEN_SECRET", "").strip().encode("utf-8")
    if not access_secret and os.getenv("ENVIRONMENT", "development").strip().lower() != "production":
        access_secret = b"development-only-access-token-secret"
    if len(access_secret) < 32:
        raise RuntimeError("ACCESS_TOKEN_SECRET debe tener al menos 32 caracteres para registrar con Google.")
    # Derive a purpose-specific key so existing deployments need no additional
    # secret rotation when OAuth registration is enabled.
    return hmac.new(access_secret, b"blocia:google-registration:v1", hashlib.sha256).digest()


class GoogleAuth:
    def __init__(self, users: UserRepository, links: ExternalLoginLinkRepository,
                 credentials: PasswordCredentialRepository | None = None):
        self.users = users
        self.links = links
        self.credentials = credentials

    def _retire_password_login(self, user):
        credential = self.credentials.get(user.mail) if self.credentials is not None else None
        if not (user.password_status or credential is not None
                or user.login_provider_status == LoginProviderStatus.PASSWORD_AND_GOOGLE):
            return user
        if self.credentials is None:
            raise RuntimeError("Password credential repository is required for Google account recovery")
        self.credentials.delete(user.mail)
        user.password_status = False
        user.auth_version += 1
        user.login_provider_status = LoginProviderStatus.GOOGLE
        return self.users.save(user)

    def complete(self, code: str, state: str, mail: str | None = None) -> tuple[User, str]:
        with getattr(self.users, "transaction", nullcontext)():
            return self._complete(code, state, mail)

    def _complete(self, code: str, state: str, mail: str | None = None) -> tuple[User, str]:
        subject = code or state
        mail = mail or (f"{subject}@gmail.com" if "@" not in subject else subject)
        link = self.links.get_by_subject("google", subject)
        if link:
            user = self.users.get(link.user_mail)
            if user is not None:
                user = self._retire_password_login(user)
                link.mark_used()
                self.links.save(link)
                return user, create_access_token(user.mail, auth_version=user.auth_version)
            raise ValueError("Google account link has no account")
        user = self.users.get(mail)
        if user is not None:
            link = ExternalLoginLink(user.mail, "google", subject, mail, user.display_name)
            if not self.links.create(link):
                existing = self.links.get_by_subject("google", subject)
                if existing and existing.user_mail == user.mail:
                    user = self.users.get(existing.user_mail)
                    if user is not None:
                        user = self._retire_password_login(user)
                        return user, create_access_token(user.mail, auth_version=user.auth_version)
                raise ValueError("Google account is already linked")
            user = self._retire_password_login(user)
            return user, create_access_token(user.mail, auth_version=user.auth_version)
        raise GoogleCompletionRequired(
            registration_token=registration_token(subject, mail),
            missing_fields=["age", "profession"],
            prefilled_fields={"mail": mail},
        )
