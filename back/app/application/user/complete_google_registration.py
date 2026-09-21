import base64
import binascii
import hashlib
import hmac
import json
import os
import time

from app.domain.user.enums import LoginProviderStatus
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.repositories import ExternalLoginLinkRepository, UserRepository
from app.domain.user.user import User
from .register_user import DuplicateMailError
from .session import create_access_token


class CompleteGoogleRegistration:
    def __init__(self, users: UserRepository, links: ExternalLoginLinkRepository):
        self.users = users
        self.links = links

    def execute(self, registration_token: str, age: int, profession: str) -> tuple[User, str]:
        if not registration_token.startswith("google:"):
            raise ValueError("Google registration token is invalid")
        try:
            encoded, signature = registration_token.removeprefix("google:").rsplit(".", 1)
            secret = os.getenv("GOOGLE_REGISTRATION_SECRET") or os.getenv("GOOGLE_CLIENT_SECRET", "development-google-registration-secret")
            expected = hmac.new(secret.encode(), encoded.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError("Google registration token signature is invalid")
            payload = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
            subject, mail = payload["subject"], payload["mail"]
            if not isinstance(subject, str) or not isinstance(mail, str) or payload.get("exp", 0) <= int(time.time()):
                raise ValueError("Google registration token is expired")
        except (KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
            raise ValueError("Google registration token is invalid")
        if self.users.exists(mail):
            raise DuplicateMailError("Mail already registered")
        user = User(mail=mail, age=age, profession=profession, password_status=False, login_provider_status=LoginProviderStatus.GOOGLE)
        self.users.save(user)
        self.links.save(ExternalLoginLink(user.mail, "google", subject, user.mail, user.display_name))
        return user, create_access_token(user.mail)
