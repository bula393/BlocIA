from app.application.chat import remote_defaults


def test_default_is_absent_without_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("BLOCIA_FREE_OPENROUTER_KEY", raising=False)
    monkeypatch.setattr(remote_defaults, "ROOT", tmp_path)
    assert remote_defaults.default_openrouter_key() is None
    assert remote_defaults.remote_free_models() == []


def test_encrypted_default_and_environment_override(tmp_path, monkeypatch):
    monkeypatch.delenv("BLOCIA_FREE_OPENROUTER_KEY", raising=False)
    monkeypatch.setattr(remote_defaults, "ROOT", tmp_path)
    remote_defaults.save_default_openrouter_key("private-test-key")
    assert b"private-test-key" not in (tmp_path / "data/.free-openrouter.token").read_bytes()
    assert remote_defaults.default_openrouter_key() == "private-test-key"
    models = remote_defaults.remote_free_models()
    assert models[0]["modelId"] == "openrouter/free"
    assert "private-test-key" not in str(models)
    monkeypatch.setenv("BLOCIA_FREE_OPENROUTER_KEY", "environment-key")
    assert remote_defaults.default_openrouter_key() == "environment-key"


def test_corrupt_credential_is_not_advertised(tmp_path, monkeypatch):
    monkeypatch.delenv("BLOCIA_FREE_OPENROUTER_KEY", raising=False)
    monkeypatch.setattr(remote_defaults, "ROOT", tmp_path)
    remote_defaults.save_default_openrouter_key("key")
    (tmp_path / "data/.free-openrouter.token").write_bytes(b"corrupt")
    assert remote_defaults.remote_free_models() == []
