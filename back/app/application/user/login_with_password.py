from app.domain.user.repositories import PasswordCredentialRepository, UserRepository
from app.domain.user.password_policy import PasswordPolicy
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
        if user is None or not user.password_status or credential is None or not credential.verify(password):
            if credential is not None:
                credential.register_invalid_attempt()
            raise InvalidCredentialsError("Invalid credentials")
        if credential.needs_rehash():
            credential.password_hash = PasswordPolicy.hash_password(password)
            self.credentials.save(credential)
        return user, create_access_token(mail, auth_version=user.auth_version)
