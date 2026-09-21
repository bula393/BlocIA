import pytest
from fastapi.testclient import TestClient

from app.domain.user.password_credential import PasswordCredential
from app.domain.user.user import User
from app.infrastructure.user.postgres_repositories import STORE
from app.main import create_app


@pytest.fixture(autouse=True)
def clean_store():
    STORE.users.clear()
    STORE.credentials.clear()
    STORE.external_links.clear()
    STORE.tokens.clear()
    STORE.seed_defaults()
    yield


@pytest.fixture
def client():
    return TestClient(create_app())


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
