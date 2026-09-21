import pytest

from app.application.user.login_with_password import InvalidCredentialsError, LoginWithPassword
from app.infrastructure.user.postgres_repositories import PasswordCredentialRepositoryImpl, UserRepositoryImpl


def test_login_success_and_safe_failure(seeded_user):
    service = LoginWithPassword(UserRepositoryImpl(), PasswordCredentialRepositoryImpl())

    user, token = service.execute(seeded_user.mail, "ClaveSegura-123")
    assert user.mail == seeded_user.mail
    assert token

    with pytest.raises(InvalidCredentialsError):
        service.execute(seeded_user.mail, "incorrecta")

    user, _ = service.execute(seeded_user.mail, "ClaveSegura-123")
    assert user.mail == seeded_user.mail
