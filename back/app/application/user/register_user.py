from contextlib import nullcontext
from app.domain.user.enums import LoginProviderStatus
from app.domain.user.password_credential import PasswordCredential
from app.domain.user.repositories import PasswordCredentialRepository, UserRepository
from app.domain.user.user import User
from .session import create_access_token


class DuplicateMailError(Exception):
    pass


class RegisterUser:
    def __init__(self, users: UserRepository, credentials: PasswordCredentialRepository, abuse_limits=None):
        self.users = users
        self.credentials = credentials
        self.abuse_limits = abuse_limits

    def execute(self, mail: str, password: str, age: int, profession: str) -> tuple[User, str]:
        with getattr(self.users, "transaction", nullcontext)():
            return self._execute(mail, password, age, profession)

    def _execute(self, mail: str, password: str, age: int, profession: str) -> tuple[User, str]:
        if self.users.exists(mail):
            raise DuplicateMailError("Mail already registered")
        if self.abuse_limits is not None:
            self.abuse_limits.admit_registration()
        user = User(mail=mail, age=age, profession=profession, password_status=True, login_provider_status=LoginProviderStatus.PASSWORD)
        credential = PasswordCredential.create(mail, password)
        if not self.users.create(user):
            raise DuplicateMailError("Mail already registered")
        self.credentials.save(credential)
        return user, create_access_token(mail)
