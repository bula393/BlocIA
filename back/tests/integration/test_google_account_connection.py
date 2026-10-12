"""OAuth lifecycle tests use real encrypted storage and simulated Google responses."""

import base64
import hashlib
import io
import json
import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from app.application.chat.ai_responder import AIResponder, AIResponseUnavailableError
from app.application.user.google_ai_client import GoogleAIClient, GoogleConnectionError
from app.application.user.google_ai_connection import GoogleAIConfig, GoogleAIConnection, GOOGLE_AI_COOKIE, GOOGLE_AI_SCOPE
from app.application.user.google_ai_credentials import GoogleAICredential
from app.application.user.list_available_models import GoogleModelsClient
from app.infrastructure.database import Database
from app.infrastructure.user.provider_oauth_repository import ProviderOAuthRepository
from app.infrastructure.user.sqlite_repositories import UserRepository
from app.presentation.user import dependencies


class GoogleDouble:
    failure = None
    refreshes = 0
    probes = 0

    def __init__(self):
        self.token = {"access_token": "private-access", "refresh_token": "private-refresh",
                      "scope": GOOGLE_AI_SCOPE, "expires_in": 3600, "id_token": "signed-id"}

    def exchange(self, config, code, verifier):
        assert code == "authorization-code" and len(verifier) >= 43
        return self.token

    def refresh(self, config, token):
        self.refreshes += 1
        if self.failure:
            raise self.failure
        return {"access_token": "rotated-access", "refresh_token": "rotated-refresh", "expires_in": 3600}

    def projects(self, token):
        return [{"projectId": "personal-project", "name": "Mi proyecto"}]

    def check_project(self, credential):
        if self.failure:
            raise self.failure

    def probe(self, credential, model_id):
        self.probes += 1
        assert credential.project_id == "personal-project"
        if self.failure:
            raise self.failure

    def revoke(self, token):
        if self.failure:
            raise self.failure


@pytest.fixture
def connection(tmp_path, monkeypatch, seeded_user):
    monkeypatch.setenv("BLOCIA_GOOGLE_OAUTH_ENABLED", "1")
    monkeypatch.setenv("GOOGLE_AI_CLIENT_ID", "google-ai-client")
    monkeypatch.setenv("GOOGLE_AI_CLIENT_SECRET", "private-client-secret")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:5173")
    database = Database(tmp_path / "oauth.sqlite3")
    UserRepository(database).save(seeded_user)
    repository = ProviderOAuthRepository(database)
    google = GoogleDouble()
    identity = {"sub": "google-subject", "email": "personal@gmail.com", "email_verified": True}
    models = SimpleNamespace(list_models=lambda credential: [SimpleNamespace(model_id="gemini-test-flash")])
    service = GoogleAIConnection(repository, google, lambda token, audience: identity, models)
    return service, google, identity, seeded_user.mail


def authorize(connection):
    service, _, identity, mail = connection
    url, browser = service.start(mail)
    params = parse_qs(urlparse(url).query)
    identity["nonce"] = params["nonce"][0]
    service.complete(mail, params["state"][0], browser, "authorization-code")
    return params, browser


def test_empty_redirect_variable_uses_public_frontend_callback(monkeypatch):
    monkeypatch.setenv("FRONTEND_URL", "https://bloqia.policloudservices.ipm.edu.ar/")
    monkeypatch.setenv("GOOGLE_AI_REDIRECT_URI", " ")
    assert GoogleAIConfig.load().redirect_uri == "https://bloqia.policloudservices.ipm.edu.ar/api/technical-profile/google/callback"


def test_pkce_transaction_bound_to_browser_user_and_consumed_once(connection):
    service, _, _, mail = connection
    url, browser = service.start(mail)
    params = parse_qs(urlparse(url).query)
    state = params["state"][0]
    repository = service.repository
    assert repository.consume("other@example.com", state, browser) is None
    assert repository.consume(mail, state, "different-browser") is None
    payload = repository.consume(mail, state, browser)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(payload["verifier"].encode()).digest()).decode().rstrip("=")
    assert params["code_challenge"] == [challenge]
    assert params["code_challenge_method"] == ["S256"]
    assert params["access_type"] == ["offline"]
    assert repository.consume(mail, state, browser) is None


def test_expired_transaction_and_replay_are_rejected(connection):
    service, _, _, mail = connection
    url, browser = service.start(mail)
    state = parse_qs(urlparse(url).query)["state"][0]
    service.repository.database.execute("UPDATE provider_oauth_transactions SET expires_at=0")
    with pytest.raises(GoogleConnectionError, match="venció"):
        service.complete(mail, state, browser, "authorization-code")
    params, browser = authorize(connection)
    with pytest.raises(GoogleConnectionError, match="venció"):
        service.complete(mail, params["state"][0], browser, "authorization-code")


@pytest.mark.parametrize("defect", ["nonce", "verified", "scope", "refresh", "cancelled"])
def test_invalid_authorization_never_saves_account(connection, defect):
    service, google, identity, mail = connection
    url, browser = service.start(mail)
    params = parse_qs(urlparse(url).query)
    identity["nonce"] = params["nonce"][0]
    if defect == "nonce":
        identity["nonce"] = "wrong-nonce"
    elif defect == "verified":
        identity["email_verified"] = False
    elif defect == "scope":
        google.token["scope"] = "openid email"
    elif defect == "refresh":
        google.token.pop("refresh_token")
    with pytest.raises(GoogleConnectionError):
        service.complete(mail, params["state"][0], browser, "authorization-code", "access_denied" if defect == "cancelled" else None)
    assert service.repository.get(mail) is None


def test_tokens_are_encrypted_and_never_exposed_in_status(connection):
    service, _, _, mail = connection
    authorize(connection)
    raw = bytes(service.repository.database.query("SELECT ciphertext FROM provider_oauth_accounts")[0][0])
    assert b"private-access" not in raw and b"private-refresh" not in raw
    status = service.status(mail)
    assert status["connected"] and not status["ready"]
    assert "private-" not in json.dumps(status)
    with pytest.raises(GoogleConnectionError, match="Elegí"):
        service.credential(mail)
    assert service.select_project(mail, "personal-project")["ready"]
    assert service.credential(mail).headers() == {"Authorization": "Bearer private-access", "x-goog-user-project": "personal-project"}


def test_only_owned_and_working_project_is_saved(connection):
    service, google, _, mail = connection
    authorize(connection)
    with pytest.raises(GoogleConnectionError) as error:
        service.select_project(mail, "someone-elses-project")
    assert error.value.status == 403 and google.probes == 0
    google.failure = GoogleConnectionError("Sin permiso", "permission", 409)
    with pytest.raises(GoogleConnectionError):
        service.select_project(mail, "personal-project")
    assert not service.status(mail)["ready"]
    google.failure = None
    assert service.select_project(mail, "personal-project")["projectName"] == "Mi proyecto"
    assert google.probes == 1


def test_refresh_rotation_is_persisted_and_reused(connection):
    service, google, _, mail = connection
    authorize(connection)
    account = service.repository.get(mail)
    account.update(project_id="personal-project", expires_at=time.time() - 1)
    service.repository.save(mail, account)
    assert service.credential(mail).access_token == "rotated-access"
    assert service.credential(mail).access_token == "rotated-access"
    assert google.refreshes == 1
    assert service.repository.get(mail)["refresh_token"] == "rotated-refresh"


def test_revoked_or_reconfigured_account_cannot_fall_back(connection, monkeypatch):
    service, google, _, mail = connection
    authorize(connection)
    account = service.repository.get(mail)
    account.update(project_id="personal-project", expires_at=0)
    service.repository.save(mail, account)
    google.failure = GoogleConnectionError("Autorización retirada", "reconnect", 409)
    with pytest.raises(GoogleConnectionError):
        service.credential(mail)
    assert service.status(mail)["needsReconnect"]
    assert not service.status(mail)["ready"]
    monkeypatch.setenv("GOOGLE_AI_CLIENT_ID", "changed-client")
    with pytest.raises(GoogleConnectionError):
        service.credential(mail)
    monkeypatch.setenv("BLOCIA_GOOGLE_OAUTH_ENABLED", "0")
    assert not service.status(mail)["available"]


def test_disconnect_removes_local_tokens_even_if_google_is_unreachable(connection):
    service, google, _, mail = connection
    authorize(connection)
    google.failure = GoogleConnectionError("Temporalmente no disponible")
    assert service.disconnect(mail) == {"disconnected": True, "revoked": False}
    assert service.credential(mail) is None
    assert not service.repository.database.query("SELECT 1 FROM provider_oauth_accounts")


def test_start_requires_verified_email_and_rejects_cross_origin(client, access_token, email_verifier, connection, verified_email):
    service, _, _, _ = connection
    client.app.dependency_overrides[dependencies.google_ai_connection] = lambda: service
    headers = {"Authorization": f"Bearer {access_token}", "Origin": "https://other-site.example"}
    assert client.post("/technical-profile/google/start", headers=headers).status_code == 403
    headers["Origin"] = "http://localhost:5173"
    response = client.post("/technical-profile/google/start", headers=headers)
    assert response.status_code == 200
    assert "HttpOnly" in response.headers["set-cookie"] and "SameSite=lax" in response.headers["set-cookie"]
    assert GOOGLE_AI_COOKIE in client.cookies
    assert "private-client-secret" not in response.text


def test_unverified_user_cannot_start_or_probe(client, access_token, email_verifier, connection):
    client.app.dependency_overrides[dependencies.google_ai_connection] = lambda: connection[0]
    headers = {"Authorization": f"Bearer {access_token}"}
    assert client.post("/technical-profile/google/start", headers=headers).status_code == 403
    assert client.post("/technical-profile/google/project", headers=headers, json={"projectId": "personal-project"}).status_code == 403
    assert connection[1].probes == 0


def test_callback_uses_browser_session_and_does_not_put_tokens_in_redirect(client, connection, seeded_user):
    from app.application.user.session import create_access_token
    service, _, identity, mail = connection
    client.app.dependency_overrides[dependencies.google_ai_connection] = lambda: service
    url, browser = service.start(mail)
    params = parse_qs(urlparse(url).query)
    identity["nonce"] = params["nonce"][0]
    client.cookies.set("bloqia_session", create_access_token(mail))
    client.cookies.set(GOOGLE_AI_COOKIE, browser)
    path = f"/technical-profile/google/callback?state={params['state'][0]}&code=authorization-code"
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "http://localhost:5173/perfil-tecnico?google=connected#provider-google"
    assert "private-" not in str(response.headers)
    assert service.status(mail)["connected"]
    assert "google=state" in client.get(path, follow_redirects=False).headers["location"]


def test_google_catalog_and_chat_send_oauth_as_bearer_with_user_project(monkeypatch):
    from app.application.user import list_available_models
    credential = GoogleAICredential("private-access", "personal-project")
    requests = []

    def catalog(request, timeout):
        requests.append(request)
        return io.BytesIO(json.dumps({"models": [{"name": "models/gemini-test", "supportedGenerationMethods": ["generateContent"]}]}).encode())

    monkeypatch.setattr(list_available_models, "urlopen", catalog)
    assert GoogleModelsClient().list_models(credential)[0].model_id == "gemini-test"
    assert requests[0].get_header("Authorization") == "Bearer private-access"
    assert requests[0].get_header("X-goog-user-project") == "personal-project"

    def respond(request):
        assert request.headers["Authorization"] == "Bearer private-access"
        assert request.headers["x-goog-user-project"] == "personal-project"
        assert "x-goog-api-key" not in request.headers
        assert "private-access" not in str(request.url)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "Respuesta"}]}}]})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert AIResponder(client).generate("google", "gemini-test", "Hola", credential) == "Respuesta"


def test_chat_google_authorization_failure_explains_account_recovery_without_echoing_provider_body():
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(403, json={"error": {"message": "private-access"}}))) as client:
        with pytest.raises(AIResponseUnavailableError, match="Volvé a conectar Google") as error:
            AIResponder(client).generate("google", "gemini-test", "Hola", GoogleAICredential("private-access", "personal-project"))
    assert "private-access" not in str(error.value)


@pytest.mark.parametrize(("status", "payload", "code"), [
    (400, {"error": "invalid_grant"}, "reconnect"),
    (403, {"error": {"message": "private-access", "details": [{"reason": "SERVICE_DISABLED"}]}}, "api-disabled"),
    (429, {"error": {"message": "private-access"}}, "quota"),
    (401, {"error": "private-access"}, "permission"),
])
def test_google_errors_are_actionable_and_do_not_echo_secrets(status, payload, code):
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, json=payload))) as client:
        with pytest.raises(GoogleConnectionError) as error:
            GoogleAIClient(client).projects("private-access")
    assert error.value.code == code and "private-access" not in str(error.value)
