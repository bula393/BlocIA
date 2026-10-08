"""Load backend-only development settings from ``back/.env.dev``."""

import os
import re
from pathlib import Path


def load_dev_environment(path: Path | None = None) -> None:
    if os.getenv("ENVIRONMENT", "development").strip().lower() == "production":
        return

    env_path = path or Path(__file__).resolve().parents[2] / ".env.dev"
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return

    for line in lines:
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        name, value = entry.split("=", 1)
        name, value = name.strip(), value.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(name, value)
