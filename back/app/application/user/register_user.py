from contextlib import nullcontext
from app.domain.user.enums import LoginProviderStatus
from app.domain.user.password_credential import PasswordCredential
from app.domain.user.repositories import PasswordCredentialRepository, UserRepository
from app.domain.user.user import User
from .session import create_access_token


class DuplicateMailError(Exception):
    pass


class RegisterUser:
    def __init__(self, users: UserRepository, credentials: PasswordCredentialRepository):
        self.users = users
        self.credentials = credentials

    def execute(self, mail: str, password: str, age: int, profession: str) -> tuple[User, str]:
        with getattr(self.users, "transaction", nullcontext)():
            return self._execute(mail, password, age, profession)

    def _execute(self, mail: str, password: str, age: int, profession: str) -> tuple[User, str]:
        if self.users.exists(mail):
            raise DuplicateMailError("Mail already registered")
        user = User(mail=mail, age=age, profession=profession, password_status=True, login_provider_status=LoginProviderStatus.PASSWORD)
        credential = PasswordCredential.create(mail, password)
        self.users.save(user)
        self.credentials.save(credential)
        return user, create_access_token(mail)
