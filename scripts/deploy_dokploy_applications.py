"""Update and request deployment of the three BlocIA Dokploy Applications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


SHA = re.compile(r"[0-9a-f]{40}")
IMAGE_PREFIX = re.compile(r"ghcr\.io/[a-z0-9][a-z0-9_.-]*/[a-z0-9][a-z0-9_.\-/]*")
APPLICATIONS = (
    ("inference", "clasificador", "DOKPLOY_CLASIFICADOR_APPLICATION_ID"),
    ("api", "back", "DOKPLOY_BACK_APPLICATION_ID"),
    ("frontend", "front", "DOKPLOY_FRONT_APPLICATION_ID"),
)


class DeploymentError(RuntimeError):
    """A safe-to-display deployment error that never includes credentials."""


def required(environment: dict[str, str], name: str) -> str:
    value = environment.get(name, "").strip()
    if not value:
        raise DeploymentError(f"Falta configurar {name}.")
    return value


def https_origin(value: str, name: str) -> str:
    try:
        parsed = urlsplit(value)
        parsed.port
        valid = (parsed.scheme == "https" and parsed.hostname and not parsed.username
                 and not parsed.password and not parsed.query and not parsed.fragment
                 and not parsed.path)
    except ValueError:
        valid = False
    if not valid:
        raise DeploymentError(f"{name} debe ser el origen HTTPS de Dokploy, sin rutas ni credenciales.")
    return value.rstrip("/")


@dataclass(frozen=True)
class Configuration:
    url: str
    api_key: str
    release: str
    image_prefix: str
    application_ids: dict[str, str]
    registry_username: str | None = None
    registry_password: str | None = None

    @classmethod
    def from_environment(cls, environment=os.environ) -> "Configuration":
        url = https_origin(required(environment, "DOKPLOY_URL"), "DOKPLOY_URL")
        release = required(environment, "RELEASE_TAG")
        prefix = required(environment, "GHCR_IMAGE_PREFIX").lower()
        if not SHA.fullmatch(release):
            raise DeploymentError("RELEASE_TAG debe ser el SHA completo del commit probado (40 caracteres).")
        if not IMAGE_PREFIX.fullmatch(prefix) or ".." in prefix or prefix.endswith("/"):
            raise DeploymentError("GHCR_IMAGE_PREFIX debe tener el formato ghcr.io/propietario/repositorio en minúsculas.")

        application_ids = {
            image_name: required(environment, variable)
            for image_name, _label, variable in APPLICATIONS
        }
        if any(not re.fullmatch(r"[A-Za-z0-9_-]+", app_id) for app_id in application_ids.values()):
            raise DeploymentError("Los IDs de las tres Applications de Dokploy tienen un formato inválido.")
        if len(set(application_ids.values())) != len(APPLICATIONS):
            raise DeploymentError("Cada servicio debe tener un ID de Application diferente en Dokploy.")

        registry_username = environment.get("GHCR_USERNAME", "").strip() or None
        registry_password = environment.get("GHCR_READ_TOKEN", "").strip() or None
        if registry_password and not registry_username:
            raise DeploymentError("GHCR_USERNAME es obligatorio si configurás GHCR_READ_TOKEN.")

        return cls(url, required(environment, "DOKPLOY_API_KEY"), release, prefix,
                   application_ids, registry_username, registry_password)


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


class DokployClient:
    def __init__(self, config: Configuration, opener=None):
        self.config = config
        self.opener = opener or build_opener(NoRedirects())

    def json_request(self, endpoint: str, *, body: dict | None = None):
        headers = {"Accept": "application/json", "Cache-Control": "no-cache",
                   "x-api-key": self.config.api_key}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(f"{self.config.url}/api/{endpoint}",
                          data=None if body is None else json.dumps(body).encode(),
                          headers=headers, method="GET" if body is None else "POST")
        try:
            with self.opener.open(request, timeout=30) as response:
                raw = response.read(1_000_001)
                if len(raw) > 1_000_000:
                    raise DeploymentError("Dokploy devolvió una respuesta demasiado grande.")
                payload = json.loads(raw) if raw else None
                if isinstance(payload, dict) and payload.get("success") is False:
                    raise DeploymentError("Dokploy rechazó una operación. Revisá los IDs y permisos de la API key.")
                return payload
        except HTTPError as error:
            raise DeploymentError(f"Dokploy rechazó la solicitud (HTTP {error.code}). Revisá los IDs y permisos de la API key.") from None
        except (URLError, OSError, ValueError):
            raise DeploymentError("No se pudo conectar o leer la respuesta de Dokploy.") from None

    def save_docker_provider(self, *, application_id: str, image: str):
        return self.json_request("application.saveDockerProvider", body={
            "applicationId": application_id,
            "dockerImage": image,
            "registryUrl": "ghcr.io",
            "username": self.config.registry_username,
            "password": self.config.registry_password,
        })

    def deploy_application(self, *, application_id: str, label: str):
        return self.json_request("application.deploy", body={
            "applicationId": application_id,
            "title": f"BlocIA {self.config.release[:12]}",
            "description": f"Despliegue automático de {label} tras CI exitoso.",
        })


def deploy_applications(config: Configuration, client: DokployClient, report: dict) -> None:
    """Update all image references first, then request deployment in dependency order."""
    report["services"] = {}
    targets = []
    for image_name, label, _variable in APPLICATIONS:
        application_id = config.application_ids[image_name]
        image = f"{config.image_prefix}-{image_name}:{config.release}"
        client.save_docker_provider(application_id=application_id, image=image)
        report["services"][label] = {"image": image, "status": "image_updated"}
        targets.append((image_name, label, application_id))

    for _image_name, label, application_id in targets:
        client.deploy_application(application_id=application_id, label=label)
        report["services"][label]["status"] = "deployment_requested"


def main() -> int:
    report = {"status": "failed", "time": datetime.now(timezone.utc).isoformat()}
    try:
        config = Configuration.from_environment()
        report["release"] = config.release
        deploy_applications(config, DokployClient(config), report)
        report["status"] = "success"
        print(f"Solicitados los despliegues de back, front y clasificador para {config.release}.")
        return 0
    except DeploymentError as error:
        report["message"] = str(error)
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        report["message"] = "Error inesperado; consultá Deployments y Logs en Dokploy."
        print(report["message"], file=sys.stderr)
        return 1
    finally:
        report_path = os.environ.get("DEPLOYMENT_REPORT_PATH", "deployment-report.json")
        try:
            with open(report_path, "w", encoding="utf-8") as output:
                json.dump(report, output, indent=2)
                output.write("\n")
        except OSError:
            print("No se pudo guardar el informe local del despliegue.", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
