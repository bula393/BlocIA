import json
import time
from types import SimpleNamespace
from urllib.parse import parse_qs

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from google.auth import crypt, jwt
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests

from app.presentation.user import auth_routes


def test_production_callback_defaults_to_public_api_route(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("FRONTEND_URL", "https://bloqia.policloudservices.ipm.edu.ar/")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "")

    assert auth_routes.callback_url() == "https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback"


def test_explicit_callback_is_preserved_and_local_default_still_works(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.delenv("GOOGLE_REDIRECT_URI", raising=False)
    assert auth_routes.callback_url() == "http://localhost:8000/auth/google/callback"
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "  https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback  ")
    assert auth_routes.callback_url() == "https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback"


def test_signed_google_result_rejects_tampering(monkeypatch):
    monkeypatch.setenv("GOOGLE_SESSION_SECRET", "test-google-session-secret")
    signed = auth_routes.encode_result({"accessToken": "private-access-token"})
    encoded, signature = signed.rsplit(".", 1)
    tampered_signature = ("0" if signature[0] != "0" else "1") + signature[1:]

    assert auth_routes.decode_result(signed) == {"accessToken": "private-access-token"}
    assert auth_routes.decode_result(f"{encoded}.{tampered_signature}") is None


@pytest.fixture
def signed_identity(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                            serialization.NoEncryption())
    public_pem = private_key.public_key().public_bytes(serialization.Encoding.PEM,
                                                      serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    signer = crypt.RSASigner.from_string(private_pem, key_id="test-google-key")
    requests = []

    def request(url, method="GET", timeout=None):
        requests.append((url, method, timeout))
        return SimpleNamespace(status=200, data=json.dumps({"test-google-key": public_pem}).encode())

    monkeypatch.setattr(google_requests, "Request", lambda: request)

    def token(**changes):
        now = int(time.time())
        claims = {"aud": "test-client", "iss": "https://accounts.google.com", "iat": now - 10,
                  "exp": now + 300, "sub": "google-subject", "email": "google@example.com",
                  "email_verified": True, "nonce": "expected-nonce"}
        claims.update(changes)
        return jwt.encode(signer, claims).decode()

    return token, requests


def test_google_id_token_signature_is_verified_with_bounded_request(signed_identity):
    token, requests = signed_identity

    identity = auth_routes.verify_google_id_token(token(), "test-client")

    assert identity["sub"] == "google-subject"
    assert len(requests) == 1
    assert requests[0][1:] == ("GET", 10)
    assert requests[0][0].startswith("https://www.googleapis.com/")


@pytest.mark.parametrize("changes", [
    {"aud": "another-client"},
    {"iss": "https://example.com"},
    {"exp": 1},
    {"iat": 9999999999, "exp": 10000000000},
])
def test_google_id_token_invalid_claims_are_rejected(signed_identity, changes):
    token, _requests = signed_identity
    with pytest.raises((ValueError, GoogleAuthError)):
        auth_routes.verify_google_id_token(token(**changes), "test-client")


def test_google_id_token_forged_signature_is_rejected(signed_identity):
    token, _requests = signed_identity
    encoded_header, encoded_payload, _signature = token().split(".")
    with pytest.raises(ValueError):
        auth_routes.verify_google_id_token(f"{encoded_header}.{encoded_payload}.Zm9yZ2Vk", "test-client")


def test_google_id_token_is_rejected_at_expiration_boundary(signed_identity):
    token, _requests = signed_identity
    with pytest.raises(ValueError):
        auth_routes.verify_google_id_token(token(exp=int(time.time())), "test-client")


def test_google_identity_exchanges_code_for_public_callback_and_expected_nonce(monkeypatch, signed_identity):
    token, _requests = signed_identity
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("FRONTEND_URL", "https://bloqia.policloudservices.ipm.edu.ar")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "")
    exchanges = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return json.dumps({"id_token": token()}).encode()

    def exchange(request, timeout):
        exchanges.append((request, timeout))
        return Response()

    monkeypatch.setattr(auth_routes, "urlopen", exchange)

    identity = auth_routes.google_identity("test-code", "expected-nonce")

    assert identity["sub"] == "google-subject"
    request, timeout = exchanges[0]
    assert request.full_url == "https://oauth2.googleapis.com/token"
    assert request.get_method() == "POST"
    assert timeout == 10
    assert parse_qs(request.data.decode())["redirect_uri"] == [
        "https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback"
    ]


@pytest.mark.parametrize("changes,nonce", [
    ({"nonce": "wrong-nonce"}, "expected-nonce"),
    ({"nonce": None}, "expected-nonce"),
    ({}, ""),
    ({"email_verified": False}, "expected-nonce"),
    ({"sub": ""}, "expected-nonce"),
    ({"email": None}, "expected-nonce"),
])
def test_google_identity_rejects_nonce_and_unverified_identity(monkeypatch, signed_identity, changes, nonce):
    token, _requests = signed_identity
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self):
            return json.dumps({"id_token": token(**changes)}).encode()

    monkeypatch.setattr(auth_routes, "urlopen", lambda *args, **kwargs: Response())
    with pytest.raises(ValueError):
        auth_routes.google_identity("test-code", nonce)
