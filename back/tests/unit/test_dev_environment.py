import os
from pathlib import Path

from app.infrastructure.dev_environment import load_dev_environment


def test_development_file_loads_values_without_overriding_process_environment(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env.dev"
    env_file.write_text(
        'BLOCIA_DEFAULT_GOOGLE_TOKEN="development-token"\n'
        "BLOCIA_DEFAULT_GROQ_TOKEN=file-token\n"
        "BLOCIA_LOCK_MINUTES=15\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("BLOCIA_DEFAULT_GOOGLE_TOKEN", raising=False)
    monkeypatch.delenv("BLOCIA_LOCK_MINUTES", raising=False)
    monkeypatch.setenv("BLOCIA_DEFAULT_GROQ_TOKEN", "process-token")

    load_dev_environment(env_file)

    assert os.environ["BLOCIA_DEFAULT_GOOGLE_TOKEN"] == "development-token"
    assert os.environ["BLOCIA_DEFAULT_GROQ_TOKEN"] == "process-token"
    assert os.environ["BLOCIA_LOCK_MINUTES"] == "15"


def test_production_does_not_load_development_file(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env.dev"
    env_file.write_text("BLOCIA_DEFAULT_OPENAI_TOKEN=development-token\n", encoding="utf-8")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("BLOCIA_DEFAULT_OPENAI_TOKEN", raising=False)

    load_dev_environment(env_file)

    assert "BLOCIA_DEFAULT_OPENAI_TOKEN" not in os.environ
