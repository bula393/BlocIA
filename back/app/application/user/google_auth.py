import base64
import hashlib
import hmac
import json
import os
import time

from app.domain.user.enums import LoginProviderStatus
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.repositories import ExternalLoginLinkRepository, UserRepository
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
    secret = os.getenv("GOOGLE_REGISTRATION_SECRET") or os.getenv("GOOGLE_CLIENT_SECRET", "development-google-registration-secret")
    signature = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"google:{encoded}.{signature}"


class GoogleAuth:
    def __init__(self, users: UserRepository, links: ExternalLoginLinkRepository):
        self.users = users
        self.links = links

    def complete(self, code: str, state: str, mail: str | None = None) -> tuple[User, str]:
        subject = code or state
        mail = mail or (f"{subject}@gmail.com" if "@" not in subject else subject)
        link = self.links.get_by_subject("google", subject)
        if link:
            link.mark_used()
            user = self.users.get(link.user_mail)
            if user is not None:
                return user, create_access_token(user.mail)
        user = self.users.get(mail)
        if user is not None:
            link = ExternalLoginLink(user.mail, "google", subject, mail, user.display_name)
            self.links.save(link)
            if user.login_provider_status == LoginProviderStatus.PASSWORD:
                user.login_provider_status = LoginProviderStatus.PASSWORD_AND_GOOGLE
                self.users.save(user)
            return user, create_access_token(user.mail)
        raise GoogleCompletionRequired(
            registration_token=registration_token(subject, mail),
            missing_fields=["age", "profession"],
            prefilled_fields={"mail": mail},
        )
