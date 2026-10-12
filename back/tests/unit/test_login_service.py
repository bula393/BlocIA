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


def test_successful_login_rehashes_legacy_password_in_place():
    import hashlib
    from app.domain.user.password_credential import PasswordCredential
    from app.domain.user.user import User
    from app.infrastructure.user.postgres_repositories import InMemoryUserStore

    store = InMemoryUserStore()
    user = User(mail="legacy@example.com", age=25, profession="Docente", password_status=True)
    legacy = PasswordCredential(user.mail, hashlib.sha256("ClaveSegura-123".encode()).hexdigest())
    store.users[user.mail] = user
    store.credentials[user.mail] = legacy

    LoginWithPassword(UserRepositoryImpl(store), PasswordCredentialRepositoryImpl(store)).execute(user.mail, "ClaveSegura-123")

    assert store.credentials[user.mail].password_hash.startswith("pbkdf2_sha256$600000$")
    assert store.credentials[user.mail].verify("ClaveSegura-123")
