"""Project quotas checked in AI Studio, bound to the credential they describe.

Google's models.list is a catalog, not an entitlement or quota endpoint.
The local snapshot must be refreshed when the project's quotas change.
"""

import hashlib
import hmac
import json
import os
from pathlib import Path

from .settings import ROOT


UNVERIFIED_GOOGLE_QUOTA = (
    "No se verificó la cuota de Google para esta clave. Revisá los límites de su "
    "proyecto en AI Studio y actualizá el registro de modelos habilitados del servidor."
)


def google_quota_models(api_key: str | None) -> set[str]:
    if not api_key:
        return set()
    path = Path(os.getenv("BLOCIA_GOOGLE_MODEL_ACCESS_PATH", str(ROOT / "data/google-model-access.json")))
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        fingerprint = hashlib.sha256(api_key.strip().encode()).hexdigest()
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get("credentialSha256"), str):
            return set()
        if not hmac.compare_digest(snapshot["credentialSha256"], fingerprint):
            return set()
        if not snapshot.get("projectId") or not snapshot.get("checkedAt"):
            return set()
        quotas = snapshot.get("models", [])
        if not isinstance(quotas, list):
            return set()
        return {
            row["modelId"] for row in quotas
            if isinstance(row, dict) and isinstance(row.get("modelId"), str)
            and row.get("chat") is True
            and all(isinstance(row.get(limit), (int, float)) and row[limit] > 0 for limit in ("rpm", "tpm", "rpd"))
        }
    except (OSError, ValueError, TypeError):
        return set()
