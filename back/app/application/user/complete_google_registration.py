import base64
from contextlib import nullcontext
import binascii
import hashlib
import hmac
import json
import time

from app.domain.user.enums import LoginProviderStatus
from app.domain.user.external_login_link import ExternalLoginLink
from app.domain.user.repositories import ExternalLoginLinkRepository, UserRepository
from app.domain.user.user import User
from .google_auth import google_registration_secret
from .register_user import DuplicateMailError
from .session import create_access_token


class CompleteGoogleRegistration:
    def __init__(self, users: UserRepository, links: ExternalLoginLinkRepository, abuse_limits=None):
        self.users = users
        self.links = links
        self.abuse_limits = abuse_limits

    def execute(self, registration_token: str, age: int, profession: str) -> tuple[User, str]:
        with getattr(self.users, "transaction", nullcontext)():
            return self._execute(registration_token, age, profession)

    def _execute(self, registration_token: str, age: int, profession: str) -> tuple[User, str]:
        if not registration_token.startswith("google:"):
            raise ValueError("Google registration token is invalid")
        try:
            encoded, signature = registration_token.removeprefix("google:").rsplit(".", 1)
            expected = hmac.new(google_registration_secret(), encoded.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise ValueError("Google registration token signature is invalid")
            payload = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode())
            subject, mail = payload["subject"], payload["mail"]
            if (not isinstance(subject, str) or not subject or not isinstance(mail, str) or not mail
                    or type(payload.get("exp")) is not int or payload["exp"] <= int(time.time())):
                raise ValueError("Google registration token is expired")
        except (KeyError, ValueError, RuntimeError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
            raise ValueError("Google registration token is invalid")
        if self.users.exists(mail):
            raise DuplicateMailError("Mail already registered")
        if self.links.get_by_subject("google", subject):
            raise DuplicateMailError("Google account already linked")
        if self.abuse_limits is not None:
            self.abuse_limits.admit_registration()
        user = User(mail=mail, age=age, profession=profession, password_status=False, login_provider_status=LoginProviderStatus.GOOGLE)
        if not self.users.create(user):
            raise DuplicateMailError("Mail already registered")
        if not self.links.create(ExternalLoginLink(user.mail, "google", subject, user.mail, user.display_name)):
            raise DuplicateMailError("Google account already linked")
        return user, create_access_token(user.mail)
