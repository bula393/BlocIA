"""Models bundled on this machine that work without a provider token."""

from importlib.util import find_spec
from pathlib import Path

from .settings import ROOT

LOCAL_MODEL_ID = "qwen3-local"
LOCAL_MODEL_PATH = ROOT / "models" / "chat"


def local_free_models() -> list[dict[str, str]]:
    required_files = ("config.json", "tokenizer.json", "model.safetensors")
    if not all((LOCAL_MODEL_PATH / filename).is_file() for filename in required_files):
        return []
    if find_spec("torch") is None or find_spec("transformers") is None:
        return []
    return [{
        "providerId": "local",
        "providerName": "En este equipo · gratis",
        "modelId": LOCAL_MODEL_ID,
        "displayName": "Qwen3-0.6B local",
    }]
