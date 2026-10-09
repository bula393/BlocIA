import pytest
from fastapi.testclient import TestClient

from app.domain.user.password_credential import PasswordCredential
from app.domain.user.user import User
from app.infrastructure.user.postgres_repositories import STORE, UserRepositoryImpl, PasswordCredentialRepositoryImpl, ExternalLoginLinkRepositoryImpl, AIProviderRepositoryImpl, AIModelRepositoryImpl, ProviderTokenRepositoryImpl, UsageEventRepositoryImpl
from app.presentation.user import dependencies
from app.main import create_app


@pytest.fixture(autouse=True)
def clean_store():
    STORE.users.clear()
    STORE.credentials.clear()
    STORE.external_links.clear()
    STORE.tokens.clear()
    STORE.token_secrets.clear()
    STORE.usage_events.clear()
    STORE.seed_defaults()
    yield


@pytest.fixture
def client():
    app = create_app()
    for dependency, repository in [(dependencies.user_repo, UserRepositoryImpl), (dependencies.credential_repo, PasswordCredentialRepositoryImpl), (dependencies.external_link_repo, ExternalLoginLinkRepositoryImpl), (dependencies.provider_repo, AIProviderRepositoryImpl), (dependencies.model_repo, AIModelRepositoryImpl), (dependencies.token_repo, ProviderTokenRepositoryImpl), (dependencies.usage_repo, UsageEventRepositoryImpl)]:
        app.dependency_overrides[dependency] = lambda repository=repository: repository(STORE)
    return TestClient(app)


@pytest.fixture
def seeded_user():
    user = User(mail="usuario.demo@example.com", age=28, profession="Estudiante", password_status=True)
    STORE.users[user.mail] = user
    STORE.credentials[user.mail] = PasswordCredential.create(user.mail, "ClaveSegura-123")
    return user


@pytest.fixture
def access_token(client, seeded_user):
    response = client.post("/auth/login", json={"mail": seeded_user.mail, "password": "ClaveSegura-123"})
    # Contract tests that request a bearer token exercise that mechanism alone.
    # Browser-session behaviour has its own explicit coverage.
    client.cookies.delete("bloqia_session")
    return response.json()["accessToken"]


@pytest.fixture
def email_verifier(client, seeded_user, tmp_path):
    from app.application.user.verify_email import VerifyEmail
    from app.infrastructure.database import Database
    from app.infrastructure.user.email_verification_repository import EmailVerificationRepository
    from app.infrastructure.user.sqlite_repositories import UserRepository

    class CaptureSender:
        def __init__(self):
            self.messages = []

        def send_verification(self, mail, code, expires_seconds):
            self.messages.append((mail, code, expires_seconds))

    database = Database(tmp_path / "verification.sqlite3")
    UserRepository(database).save(seeded_user)
    sender = CaptureSender()
    clock = [1800000000.0]
    verifier = VerifyEmail(EmailVerificationRepository(database), sender, "test-verification-secret-at-least-32-characters", lambda: clock[0])
    client.app.dependency_overrides[dependencies.email_verification] = lambda: verifier
    return verifier, sender, clock


@pytest.fixture
def verified_email(client, access_token, email_verifier):
    headers = {"Authorization": f"Bearer {access_token}"}
    assert client.post("/technical-profile/email-verification/request", headers=headers).status_code == 200
    code = email_verifier[1].messages[-1][1]
    assert client.post("/technical-profile/email-verification/confirm", headers=headers, json={"code": code}).status_code == 200
