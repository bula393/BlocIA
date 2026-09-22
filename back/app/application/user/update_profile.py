from contextlib import nullcontext
from dataclasses import replace
from app.domain.user.repositories import UserRepository
from app.domain.user.user import User
from .get_profile import ProfileNotFoundError


class UpdateProfile:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, mail: str, age: int | None = None, profession: str | None = None, display_name: str | None = None) -> User:
        with getattr(self.users, "transaction", nullcontext)():
            return self._execute(mail, age, profession, display_name)

    def _execute(self, mail: str, age: int | None = None, profession: str | None = None, display_name: str | None = None) -> User:
        user = self.users.get(mail)
        if user is None:
            raise ProfileNotFoundError("Profile not found")
        user = replace(user)
        user.update_profile(age=age, profession=profession, display_name=display_name)
        self.users.save(user)
        return user
