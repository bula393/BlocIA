import hashlib
import json

import pytest

from app.application.chat.google_model_access import google_quota_models


def snapshot(path, key="test-key"):
    path.write_text(json.dumps({
        "credentialSha256": hashlib.sha256(key.encode()).hexdigest(),
        "projectId": "test-project", "checkedAt": "2026-10-06T00:00:00Z",
        "models": [
            {"modelId": "flash", "chat": True, "rpm": 5, "tpm": 250000, "rpd": 20},
            {"modelId": "pro", "chat": True, "rpm": 0, "tpm": 0, "rpd": 0},
            {"modelId": "audio", "chat": False, "rpm": 5, "tpm": 250000, "rpd": 20},
            {"modelId": "exhausted", "chat": True, "rpm": 5, "tpm": 250000, "rpd": 0},
        ],
    }), encoding="utf-8")


def test_quota_requires_chat_and_all_positive_limits(tmp_path, monkeypatch):
    path = tmp_path / "quotas.json"
    snapshot(path)
    monkeypatch.setenv("BLOCIA_GOOGLE_MODEL_ACCESS_PATH", str(path))
    assert google_quota_models("test-key") == {"flash"}
    assert google_quota_models("another-key") == set()
    assert google_quota_models(None) == set()


@pytest.mark.parametrize("content", [None, "bad-json", "[]", '{"credentialSha256": 123}', '{"credentialSha256":"wrong"}'])
def test_missing_or_invalid_snapshot_does_not_grant_access(tmp_path, monkeypatch, content):
    path = tmp_path / "quotas.json"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("BLOCIA_GOOGLE_MODEL_ACCESS_PATH", str(path))
    assert google_quota_models("test-key") == set()
