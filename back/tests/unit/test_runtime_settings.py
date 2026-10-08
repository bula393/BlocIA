from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from app.infrastructure.runtime_settings import RuntimeSettings
from app.presentation.health_routes import local_models
from app.main import create_app


def production_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("FRONTEND_URL", "https://blocia.example.com")
    monkeypatch.setenv("ACCESS_TOKEN_SECRET", "a" * 40)
    monkeypatch.setenv("BLOCIA_INFERENCE_URL", "http://inference:8001")
    monkeypatch.setenv("BLOCIA_INFERENCE_TOKEN", "b" * 40)


@pytest.mark.parametrize("name,value", [("ACCESS_TOKEN_SECRET", "short"), ("FRONTEND_URL", "http://example.com"),
                                       ("FRONTEND_URL", "https://example.com/path"), ("BLOCIA_INFERENCE_TOKEN", "")])
def test_incomplete_production_configuration_fails_before_serving(monkeypatch, name, value):
    production_environment(monkeypatch)
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError, match=name):
        create_app()


def test_readiness_requires_classifier_and_exposes_release_only(monkeypatch, tmp_path):
    from app.infrastructure.database import Database, get_database
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("RELEASE_TAG", "abc123")
    app = create_app()
    app.dependency_overrides[get_database] = lambda: Database(tmp_path / "ready.sqlite3")
    app.dependency_overrides[local_models] = lambda: SimpleNamespace(status=lambda: {"classifierReady": False, "private": "secret"})
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"ready": False, "databaseReady": True, "classifierReady": False, "release": "abc123"}
    app.dependency_overrides[local_models] = lambda: SimpleNamespace(status=lambda: {"classifierReady": True})
    assert client.get("/ready").json()["ready"] is True


def test_readiness_includes_the_private_inference_release_when_available(monkeypatch, tmp_path):
    from app.infrastructure.database import Database, get_database
    monkeypatch.setenv("ENVIRONMENT", "development")
    app = create_app()
    app.dependency_overrides[get_database] = lambda: Database(tmp_path / "ready.sqlite3")
    app.dependency_overrides[local_models] = lambda: SimpleNamespace(status=lambda: {"classifierReady": True, "release": "a" * 40})
    assert TestClient(app).get("/ready").json()["inferenceRelease"] == "a" * 40
