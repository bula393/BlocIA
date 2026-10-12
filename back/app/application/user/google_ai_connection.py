"""Connect a Google account without changing the user's BloqIA login."""

import base64
from dataclasses import dataclass, field
import hashlib
import os
import re
import secrets
import time
from urllib.parse import urlencode

from .google_ai_client import GoogleAIClient, GoogleConnectionError
from .google_ai_credentials import GoogleAICredential

GOOGLE_AI_SCOPE = "https://www.googleapis.com/auth/cloud-platform"
GOOGLE_AI_COOKIE = "bloqia_google_ai_transaction"


@dataclass(frozen=True)
class GoogleAIConfig:
    client_id: str
    client_secret: str = field(repr=False)
    redirect_uri: str
    enabled: bool

    @classmethod
    def load(cls):
        origin = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
        return cls(os.getenv("GOOGLE_AI_CLIENT_ID", "").strip(), os.getenv("GOOGLE_AI_CLIENT_SECRET", "").strip(),
                   os.getenv("GOOGLE_AI_REDIRECT_URI", "").strip() or f"{origin}/api/technical-profile/google/callback",
                   os.getenv("BLOCIA_GOOGLE_OAUTH_ENABLED", "0") == "1")

    @property
    def available(self):
        return bool(self.enabled and self.client_id and self.client_secret)


class GoogleAIConnection:
    def __init__(self, repository, client=None, verify_identity=None, models_client=None):
        self.repository = repository
        self.client = client or GoogleAIClient()
        self.verify_identity = verify_identity
        self.models_client = models_client

    def status(self, mail):
        account = self.repository.get(mail)
        config = GoogleAIConfig.load()
        reconnect = bool(account and (account.get("needs_reconnect") or account.get("client_id") != config.client_id))
        return {"available": config.available, "connected": bool(account),
                "email": account.get("email") if account else None,
                "projectId": account.get("project_id") if account else None,
                "projectName": account.get("project_name") if account else None,
                "ready": bool(config.available and account and account.get("project_id") and not reconnect),
                "needsReconnect": reconnect}

    def start(self, mail):
        config = GoogleAIConfig.load()
        if not config.available:
            raise GoogleConnectionError("La conexión con Google todavía no está habilitada en BloqIA. Podés usar la conexión del proyecto mientras tanto.", "configuration", 503)
        state, browser, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(4))
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        self.repository.begin(mail, state, browser, {"nonce": nonce, "verifier": verifier})
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "client_id": config.client_id, "redirect_uri": config.redirect_uri,
            "response_type": "code", "scope": f"openid email {GOOGLE_AI_SCOPE}",
            "state": state, "nonce": nonce, "code_challenge": challenge, "code_challenge_method": "S256",
            "access_type": "offline", "prompt": "consent select_account",
        })
        return url, browser

    def complete(self, mail, state, browser, code, error=None):
        transaction = self.repository.consume(mail, state, browser)
        if not transaction:
            raise GoogleConnectionError("Esta conexión venció o no corresponde a tu sesión. Volvé a empezar.", "state", 400)
        if error or not code or len(code) > 4096:
            raise GoogleConnectionError("Cancelaste la conexión con Google. Podés volver a intentarlo cuando quieras.", "cancelled", 400)
        config = GoogleAIConfig.load()
        if not config.available:
            raise GoogleConnectionError("La conexión con Google no está habilitada.", "configuration", 503)
        token = self.client.exchange(config, code, transaction["verifier"])
        verify = self.verify_identity
        if verify is None:
            from app.presentation.user.auth_routes import verify_google_id_token
            verify = verify_google_id_token
        try:
            identity = verify(token.get("id_token", ""), config.client_id)
            if not identity.get("sub") or not isinstance(identity.get("email"), str) or identity.get("email_verified") not in (True, "true") or not secrets.compare_digest(str(identity.get("nonce", "")), transaction["nonce"]):
                raise ValueError("invalid identity")
        except Exception:
            raise GoogleConnectionError("No pudimos verificar esta cuenta de Google. Volvé a conectarla.", "permission", 400) from None
        if GOOGLE_AI_SCOPE not in token.get("scope", "").split() or not token.get("access_token") or not token.get("refresh_token"):
            raise GoogleConnectionError("Falta autorizar el acceso a Google Cloud. Volvé a conectar la cuenta y revisá los permisos que solicita Google.", "permission", 400)
        with self.repository.locked(mail):
            self.repository.save(mail, {"subject": identity["sub"], "email": identity["email"],
                "access_token": token["access_token"], "refresh_token": token["refresh_token"],
                "expires_at": time.time() + int(token.get("expires_in", 3600)),
                "scope": token["scope"], "client_id": config.client_id})

    def _fresh(self, mail):
        config = GoogleAIConfig.load()
        failure = None
        with self.repository.locked(mail) as account:
            if not account:
                raise GoogleConnectionError("Conectá tu cuenta de Google para continuar.", "reconnect", 409)
            if not config.available or account.get("client_id") != config.client_id or account.get("needs_reconnect"):
                raise GoogleConnectionError("Volvé a conectar tu cuenta de Google para continuar.", "reconnect", 409)
            if account["expires_at"] <= time.time() + 60:
                try:
                    token = self.client.refresh(config, account["refresh_token"])
                    if not token.get("access_token") or GOOGLE_AI_SCOPE not in token.get("scope", account["scope"]).split():
                        raise GoogleConnectionError("Volvé a autorizar el acceso a Google.", "reconnect", 409)
                    account.update(access_token=token["access_token"], expires_at=time.time() + int(token.get("expires_in", 3600)))
                    if token.get("refresh_token"):
                        account["refresh_token"] = token["refresh_token"]
                    self.repository.save(mail, account)
                except GoogleConnectionError as exc:
                    failure = exc
                    if exc.code == "reconnect":
                        account["needs_reconnect"] = True
                        self.repository.save(mail, account)
        if failure:
            raise failure
        return account

    def projects(self, mail):
        return self.client.projects(self._fresh(mail)["access_token"])

    def select_project(self, mail, project_id):
        if not re.fullmatch(r"[a-z][a-z0-9-]{4,61}[a-z0-9]", project_id):
            raise GoogleConnectionError("Elegí uno de los proyectos de tu cuenta.", "project", 422)
        account = self._fresh(mail)
        project = next((item for item in self.client.projects(account["access_token"]) if item["projectId"] == project_id), None)
        if not project:
            raise GoogleConnectionError("Este proyecto no está disponible para tu cuenta. Actualizá la lista y volvé a elegir.", "project", 403)
        credential = GoogleAICredential(account["access_token"], project_id)
        self.client.check_project(credential)
        from .list_available_models import GoogleModelsClient, ProviderModelsUnavailableError
        try:
            models = (self.models_client or GoogleModelsClient()).list_models(credential)
        except ProviderModelsUnavailableError:
            raise GoogleConnectionError("No pudimos consultar los modelos de Gemini. Revisá el acceso del proyecto y volvé a comprobarlo.", "project", 409) from None
        models = [model for model in models if re.fullmatch(r"[A-Za-z0-9._-]+", model.model_id)]
        if not models:
            raise GoogleConnectionError("Google no ofrece modelos de texto para este proyecto.", "project", 409)
        flash = [model for model in models if "flash" in model.model_id and "preview" not in model.model_id]
        probe = next((model for model in flash if model.model_id == "gemini-3.8-flash"), (flash or models)[0])
        self.client.probe(credential, probe.model_id)
        with self.repository.locked(mail) as current:
            if not current or current["subject"] != account["subject"] or current["refresh_token"] != account["refresh_token"]:
                raise GoogleConnectionError("La cuenta cambió mientras comprobábamos el proyecto. Volvé a intentarlo.", "reconnect", 409)
            current.update(project_id=project_id, project_name=project["name"], checked_at=time.time())
            self.repository.save(mail, current)
        return self.status(mail)

    def credential(self, mail):
        if not self.repository.get(mail):
            return None
        account = self._fresh(mail)
        if not account.get("project_id"):
            raise GoogleConnectionError("Tu cuenta Google está conectada. Elegí y comprobá un proyecto en Proveedores para usar Gemini.", "project", 409)
        return GoogleAICredential(account["access_token"], account["project_id"])

    def disconnect(self, mail):
        # Delete locally even if Google's revocation endpoint is temporarily down.
        revoked = True
        with self.repository.locked(mail) as account:
            if account:
                try:
                    self.client.revoke(account["refresh_token"])
                except GoogleConnectionError:
                    revoked = False
                self.repository.delete(mail)
        return {"disconnected": True, "revoked": revoked}
