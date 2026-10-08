from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import main


def test_models_warm_before_requests_and_transport_closes_on_shutdown(monkeypatch):
    events = []
    monkeypatch.setenv("BLOCIA_PRELOAD_CLASSIFIER", "1")
    monkeypatch.setenv("BLOCIA_PRELOAD_LOCAL_CHAT", "1")
    monkeypatch.setattr(main, "local_models", lambda: SimpleNamespace(warmup=lambda: events.append("classifier")))
    monkeypatch.setattr(main, "local_text_model", lambda: SimpleNamespace(warmup=lambda: events.append("local")))
    monkeypatch.setattr(main, "ai_responder", lambda: SimpleNamespace(close=lambda: events.append("closed")))
    with TestClient(main.create_app()) as client:
        assert events == ["classifier", "local"]
        assert client.get("/openapi.json").status_code == 200
    assert events == ["classifier", "local", "closed"]


def test_unavailable_classifier_does_not_prevent_startup_or_log_user_text(monkeypatch, caplog):
    def unavailable():
        raise RuntimeError("private-prompt")

    monkeypatch.setenv("BLOCIA_PRELOAD_CLASSIFIER", "1")
    monkeypatch.setattr(main, "local_models", lambda: SimpleNamespace(warmup=unavailable))
    monkeypatch.setattr(main, "ai_responder", lambda: SimpleNamespace(close=lambda: None))
    with TestClient(main.create_app()) as client:
        assert client.get("/openapi.json").status_code == 200
    assert "private-prompt" not in caplog.text
