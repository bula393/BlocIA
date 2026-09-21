from app.domain.user.repositories import UserRepository
from app.domain.user.user import User


class ProfileNotFoundError(Exception):
    pass


class GetProfile:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, mail: str) -> User:
        user = self.users.get(mail)
        if user is None:
            raise ProfileNotFoundError("Profile not found")
        return user
