import base64
import binascii
import hashlib
import hmac
import json
import os
import time


# The browser cookie itself has no expiry (it is discarded when the browser is
# closed).  The signed credential still has a bounded lifetime in case it is
# copied from a live browser session.
ACCESS_TOKEN_TTL_SECONDS = 24 * 60 * 60


def _base64_url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64_url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _token_secret() -> bytes:
    secret = os.getenv("ACCESS_TOKEN_SECRET")
    if secret:
        return secret.encode("utf-8")
    if os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError("ACCESS_TOKEN_SECRET must be configured in production")
    return b"development-only-access-token-secret"


def create_access_token(mail: str, expires_in_seconds: int = ACCESS_TOKEN_TTL_SECONDS, *, auth_version: int = 0) -> str:
    now = int(time.time())
    header = _base64_url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _base64_url_encode(json.dumps({"sub": mail, "iat": now, "exp": now + expires_in_seconds, "ver": auth_version}, separators=(",", ":")).encode())
    signed = f"{header}.{payload}"
    signature = _base64_url_encode(hmac.new(_token_secret(), signed.encode("ascii"), hashlib.sha256).digest())
    return f"{signed}.{signature}"


def parse_access_token_claims(token: str) -> dict | None:
    try:
        header, encoded_payload, signature = token.split(".")
        signed = f"{header}.{encoded_payload}"
        expected = _base64_url_encode(hmac.new(_token_secret(), signed.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        metadata = json.loads(_base64_url_decode(header))
        payload = json.loads(_base64_url_decode(encoded_payload))
        if not isinstance(metadata, dict) or not isinstance(payload, dict):
            return None
        subject = payload.get("sub")
        version = payload.get("ver", 0)
        if (metadata.get("alg") != "HS256" or not isinstance(subject, str) or not subject
                or type(version) is not int or version < 0 or payload.get("exp", 0) <= int(time.time())):
            return None
        return payload
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
        return None


def parse_access_token(token: str) -> str | None:
    claims = parse_access_token_claims(token)
    return claims.get("sub") if claims else None
