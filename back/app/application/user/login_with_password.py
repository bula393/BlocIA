from app.domain.user.repositories import PasswordCredentialRepository, UserRepository
from .session import create_access_token


class InvalidCredentialsError(Exception):
    pass


class LoginWithPassword:
    def __init__(self, users: UserRepository, credentials: PasswordCredentialRepository):
        self.users = users
        self.credentials = credentials

    def execute(self, mail: str, password: str) -> tuple[object, str]:
        user = self.users.get(mail)
        credential = self.credentials.get(mail)
        if user is None or credential is None or not credential.verify(password):
            if credential is not None:
                credential.register_invalid_attempt()
            raise InvalidCredentialsError("Invalid credentials")
        return user, create_access_token(mail)
