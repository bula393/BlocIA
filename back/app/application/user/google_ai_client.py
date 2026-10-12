"""Fixed Google endpoints for account authorization and Gemini access."""

import httpx

from .google_ai_credentials import GoogleAICredential


class GoogleConnectionError(Exception):
    def __init__(self, message, code="unavailable", status=502):
        super().__init__(message)
        self.code = code
        self.status = status


class GoogleAIClient:
    def __init__(self, client=None):
        self.client = client

    def request(self, method, url, **kwargs):
        try:
            if self.client:
                response = self.client.request(method, url, timeout=20, **kwargs)
            else:
                with httpx.Client(timeout=20) as client:
                    response = client.request(method, url, **kwargs)
            if response.status_code >= 400:
                self._error(response)
            payload = response.json() if response.content else {}
            if not isinstance(payload, dict):
                raise ValueError("invalid response")
            return payload
        except GoogleConnectionError:
            raise
        except (httpx.RequestError, ValueError):
            raise GoogleConnectionError("No pudimos comunicarnos con Google. Volvé a intentarlo.") from None

    @staticmethod
    def _error(response):
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        error = payload.get("error") if isinstance(payload, dict) else None
        if error == "invalid_grant":
            raise GoogleConnectionError("La autorización de Google venció o fue retirada. Volvé a conectar tu cuenta.", "reconnect", 409)
        details = error.get("details", []) if isinstance(error, dict) else []
        reasons = {row.get("reason") for row in details if isinstance(row, dict)} if isinstance(details, list) else set()
        if "SERVICE_DISABLED" in reasons:
            raise GoogleConnectionError("Este proyecto todavía no tiene habilitado el servicio de Google necesario. Abrí la configuración del proyecto y habilitalo.", "api-disabled", 409)
        if response.status_code == 429:
            raise GoogleConnectionError("Google no tiene cupo disponible para esta prueba. Revisá los límites del proyecto o intentá más tarde.", "quota", 409)
        if response.status_code in (401, 403):
            raise GoogleConnectionError("Google no autorizó el acceso. Revisá los permisos de la cuenta y del proyecto, o volvé a conectarla.", "permission", 409)
        if response.status_code == 404:
            raise GoogleConnectionError("Google no encontró este proyecto o servicio. Actualizá los proyectos y volvé a elegir.", "project", 409)
        raise GoogleConnectionError("Google no pudo completar la conexión. Volvé a intentarlo.")

    def exchange(self, config, code, verifier):
        return self.request("POST", "https://oauth2.googleapis.com/token", data={
            "client_id": config.client_id, "client_secret": config.client_secret,
            "redirect_uri": config.redirect_uri, "code": code,
            "code_verifier": verifier, "grant_type": "authorization_code",
        })

    def refresh(self, config, refresh_token):
        return self.request("POST", "https://oauth2.googleapis.com/token", data={
            "client_id": config.client_id, "client_secret": config.client_secret,
            "refresh_token": refresh_token, "grant_type": "refresh_token",
        })

    def projects(self, access_token):
        result = []
        page_token = None
        for _ in range(10):
            params = {"filter": "lifecycleState:ACTIVE", "pageSize": 100}
            if page_token:
                params["pageToken"] = page_token
            payload = self.request("GET", "https://cloudresourcemanager.googleapis.com/v1/projects", headers={"Authorization": f"Bearer {access_token}"}, params=params)
            for project in payload.get("projects", []):
                if isinstance(project, dict) and project.get("projectId") and project.get("lifecycleState") == "ACTIVE":
                    result.append({"projectId": project["projectId"], "name": project.get("name") or project["projectId"]})
            page_token = payload.get("nextPageToken")
            if not page_token:
                return result
        raise GoogleConnectionError("Tu cuenta tiene muchos proyectos. Usá una cuenta con acceso al proyecto de Gemini que querés conectar.", "project", 409)

    def check_project(self, credential: GoogleAICredential):
        headers = credential.headers()
        permissions = self.request("POST", f"https://cloudresourcemanager.googleapis.com/v1/projects/{credential.project_id}:testIamPermissions", headers={"Authorization": headers["Authorization"]}, json={"permissions": ["serviceusage.services.use"]})
        if "serviceusage.services.use" not in permissions.get("permissions", []):
            raise GoogleConnectionError("Tu cuenta puede ver este proyecto, pero no usar sus servicios. Elegí otro proyecto o pedí acceso a su administrador.", "permission", 409)
        service = self.request("GET", f"https://serviceusage.googleapis.com/v1/projects/{credential.project_id}/services/generativelanguage.googleapis.com", headers={"Authorization": headers["Authorization"]})
        if service.get("state") != "ENABLED":
            raise GoogleConnectionError("Habilitá Gemini en este proyecto y volvé a comprobar la conexión.", "api-disabled", 409)

    def probe(self, credential: GoogleAICredential, model_id):
        # The user explicitly requests this small, potentially billable check.
        return self.request("POST", f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent", headers=credential.headers(), json={
            "contents": [{"parts": [{"text": "Respond only OK."}]}],
            "generationConfig": {"maxOutputTokens": 8},
        })

    def revoke(self, token):
        return self.request("POST", "https://oauth2.googleapis.com/revoke", data={"token": token})
