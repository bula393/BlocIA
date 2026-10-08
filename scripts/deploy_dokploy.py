"""Deploy a tested release to three independent Dokploy Compose services.

Only RELEASE_TAG and GHCR_IMAGE_PREFIX are replaced in Dokploy's environment.
Credentials and persistent volumes are preserved. No response bodies are logged.
"""

import argparse
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


MARKER = re.compile(r"^x-blocia-deployment:\s*1\s*$", re.MULTILINE)
SHA = re.compile(r"[0-9a-f]{40}")
IMAGE_PREFIX = re.compile(r"ghcr\.io/[a-z0-9][a-z0-9_.-]*/[a-z0-9][a-z0-9_.\-/]*")
SERVICES = ("inference", "api", "frontend")


class DeploymentError(RuntimeError):
    """A message safe to display in public CI output."""


def required(environment, name):
    value = environment.get(name, "").strip()
    if not value:
        raise DeploymentError(f"Falta configurar {name}.")
    return value


def https_url(value, name):
    try:
        parsed = urlsplit(value)
        parsed.port
        valid = (parsed.scheme == "https" and parsed.hostname and not parsed.username
                 and not parsed.password and not parsed.query and not parsed.fragment)
    except ValueError:
        valid = False
    if not valid:
        raise DeploymentError(f"{name} debe ser una URL HTTPS sin credenciales ni parámetros.")
    return value.rstrip("/")


@dataclass(frozen=True)
class Configuration:
    url: str
    compose_id: str
    api_key: str
    release: str
    image_prefix: str
    health_url: str
    version_url: str
    timeout: int = 1800
    service: str | None = None

    @classmethod
    def from_environment(cls, environment=os.environ):
        url = https_url(required(environment, "DOKPLOY_URL"), "DOKPLOY_URL")
        if urlsplit(url).path:
            raise DeploymentError("DOKPLOY_URL debe ser el origen de Dokploy, sin /api ni otras rutas.")
        release = required(environment, "RELEASE_TAG")
        prefix = required(environment, "GHCR_IMAGE_PREFIX")
        if not SHA.fullmatch(release):
            raise DeploymentError("RELEASE_TAG debe ser el SHA completo del commit probado (40 caracteres).")
        if not IMAGE_PREFIX.fullmatch(prefix) or ".." in prefix or prefix.endswith("/"):
            raise DeploymentError("GHCR_IMAGE_PREFIX debe tener el formato ghcr.io/propietario/repositorio en minúsculas.")
        health = https_url(required(environment, "PUBLIC_HEALTH_URL"), "PUBLIC_HEALTH_URL")
        version = https_url(required(environment, "FRONTEND_VERSION_URL"), "FRONTEND_VERSION_URL")
        if urlsplit(health).netloc != urlsplit(version).netloc:
            raise DeploymentError("Las comprobaciones de API y frontend deben usar el mismo dominio público.")
        try:
            timeout = int(environment.get("DEPLOY_TIMEOUT_SECONDS", "1800"))
        except ValueError:
            raise DeploymentError("DEPLOY_TIMEOUT_SECONDS debe ser un número entero.") from None
        if not 30 <= timeout <= 7200:
            raise DeploymentError("DEPLOY_TIMEOUT_SECONDS debe estar entre 30 y 7200.")
        return cls(url, required(environment, "DOKPLOY_COMPOSE_ID"), required(environment, "DOKPLOY_API_KEY"),
                   release, prefix, health, version, timeout)


@dataclass(frozen=True)
class DeploymentPlan:
    services: tuple[Configuration, ...]

    @classmethod
    def from_environment(cls, environment=os.environ):
        configurations = []
        for service in SERVICES:
            identifier = required(environment, f"DOKPLOY_{service.upper()}_COMPOSE_ID")
            config = Configuration.from_environment({**environment, "DOKPLOY_COMPOSE_ID": identifier})
            configurations.append(replace(config, service=service))
        if len({config.compose_id for config in configurations}) != len(SERVICES):
            raise DeploymentError("Cada servicio debe tener un composeId diferente en Dokploy.")
        return cls(tuple(configurations))


def update_environment(existing, release, prefix):
    """Keep every unrelated dotenv line verbatim, including multiline secrets."""
    replacements = {"RELEASE_TAG": release, "GHCR_IMAGE_PREFIX": prefix}
    lines = []
    seen = set()
    open_quote = None
    for line in existing.splitlines(keepends=True):
        if open_quote:
            lines.append(line)
            if re.search(rf"(?<!\\){re.escape(open_quote)}", line):
                open_quote = None
            continue
        match = re.match(r"^[ \t]*(?:export[ \t]+)?(RELEASE_TAG|GHCR_IMAGE_PREFIX)[ \t]*=", line)
        if match:
            name = match.group(1)
            if name not in seen:
                lines.append(f"{name}={replacements[name]}\n")
                seen.add(name)
        else:
            lines.append(line)
            assignment = re.match(r"^[ \t]*(?:export[ \t]+)?[A-Za-z_][A-Za-z0-9_]*[ \t]*=(.*)", line)
            if assignment:
                value = assignment.group(1).lstrip()
                if value.startswith(("'", '"')) and not re.search(rf"(?<!\\){re.escape(value[0])}", value[1:]):
                    open_quote = value[0]
    if open_quote:
        raise DeploymentError("Las variables de Dokploy contienen un valor entre comillas sin cerrar.")
    if lines and not lines[-1].endswith(("\n", "\r")):
        lines.append("\n")
    for name, value in replacements.items():
        if name not in seen:
            lines.append(f"{name}={value}\n")
    return "".join(lines)


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


class DokployClient:
    def __init__(self, config, opener=None):
        self.config = config
        self.opener = opener or build_opener(NoRedirects())

    def json_request(self, url, *, body=None, authenticated=False):
        headers = {"Accept": "application/json", "Cache-Control": "no-cache"}
        if authenticated:
            headers["x-api-key"] = self.config.api_key
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(url, data=None if body is None else json.dumps(body).encode(), headers=headers,
                          method="GET" if body is None else "POST")
        try:
            with self.opener.open(request, timeout=15) as response:
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise DeploymentError("Respuesta de despliegue demasiado grande.")
                payload = json.loads(raw) if raw else None
                if body is None and not isinstance(payload, dict):
                    raise DeploymentError("Respuesta de despliegue inválida.")
                if isinstance(payload, dict) and payload.get("success") is False:
                    raise DeploymentError("Dokploy rechazó la operación de despliegue.")
                return payload
        except HTTPError as error:
            raise DeploymentError(f"La comprobación HTTP falló (estado {error.code}). Revisá los registros del servicio.") from None
        except (URLError, OSError, ValueError):
            raise DeploymentError("No se pudo conectar o leer la respuesta de despliegue.") from None

    def compose(self):
        query = urlencode({"composeId": self.config.compose_id})
        return self.json_request(f"{self.config.url}/api/compose.one?{query}", authenticated=True)

    def update(self, body):
        return self.json_request(f"{self.config.url}/api/compose.update", body=body, authenticated=True)

    def start(self):
        return self.json_request(f"{self.config.url}/api/compose.deploy", authenticated=True,
                                 body={"composeId": self.config.compose_id,
                                       "title": f"GitHub {self.config.release[:12]}", "freshVolumes": False})

    def release_ready(self):
        try:
            health = self.json_request(self.config.health_url)
            version = self.json_request(self.config.version_url)
            return (health.get("ready") is True and health.get("release") == self.config.release
                    and version.get("release") == self.config.release
                    and (self.config.service is None or health.get("inferenceRelease") == self.config.release))
        except DeploymentError:
            return False


def validate_target(config, compose_file, current):
    if not MARKER.search(compose_file):
        raise DeploymentError("El archivo local no es el Compose de BlocIA esperado.")
    if (current.get("sourceType") != "raw" or current.get("composeType", "docker-compose") != "docker-compose"
            or not isinstance(current.get("composeFile"), str) or not MARKER.search(current["composeFile"])):
        raise DeploymentError("El composeId debe corresponder al servicio Raw de BlocIA creado con su archivo Compose.")
    if config.service:
        role = re.compile(rf"^x-blocia-service:\s*{re.escape(config.service)}\s*$", re.MULTILINE)
        if not role.search(compose_file) or not role.search(current["composeFile"]):
            raise DeploymentError(f"El composeId o el archivo no corresponden al servicio {config.service}.")
    if not isinstance(current.get("env"), str):
        raise DeploymentError("Completá primero las variables del servicio en Dokploy.")


def deploy(config, compose_file, client, *, current=None, verify_release=True, clock=time.monotonic, sleep=time.sleep):
    current = client.compose() if current is None else current
    validate_target(config, compose_file, current)
    new_environment = update_environment(current["env"], config.release, config.image_prefix)
    client.update({"composeId": config.compose_id, "composeFile": compose_file,
                   "env": new_environment, "autoDeploy": False})
    client.start()
    started = clock()
    seen_running = False
    while clock() - started < config.timeout:
        status = client.compose().get("composeStatus")
        seen_running = seen_running or status == "running"
        if status == "error" and (seen_running or clock() - started >= 30):
            raise DeploymentError("Dokploy informó un error. Consultá Deployments y Logs; los volúmenes se conservaron.")
        if status == "done" and (not verify_release or client.release_ready()):
            return
        sleep(10)
    raise DeploymentError("Se agotó el tiempo esperando esta versión y la IA lista. Revisá imágenes, dominio y registros de Dokploy.")


def environment_value(environment, name, default=""):
    """Read simple shared settings, ignoring assignments inside multiline values."""
    result = default
    open_quote = None
    for line in environment.splitlines():
        if open_quote:
            if re.search(rf"(?<!\\){re.escape(open_quote)}", line):
                open_quote = None
            continue
        match = re.match(r"^[ \t]*(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)[ \t]*=(.*)", line)
        if not match:
            continue
        key, raw = match.groups()
        raw = raw.strip()
        if raw.startswith(("'", '"')):
            closing = re.search(rf"(?<!\\){re.escape(raw[0])}", raw[1:])
            if closing is None:
                open_quote = raw[0]
                if key == name:
                    raise DeploymentError(f"{name} debe tener un valor de una sola línea.")
                continue
            value = raw[1:closing.start() + 1]
        else:
            value = re.split(r"[ \t]+#", raw, maxsplit=1)[0].rstrip()
        if key == name:
            result = value or default
    return result


def deploy_services(plan, compose_files, clients, report, *, clock=time.monotonic, sleep=time.sleep):
    """Preflight every resource before writes, then deploy dependencies in order."""
    snapshots = {}
    for config in plan.services:
        snapshots[config.service] = clients[config.service].compose()
        validate_target(config, compose_files[config.service], snapshots[config.service])
    if len({snapshot.get("serverId") for snapshot in snapshots.values()}) != 1:
        raise DeploymentError("Los tres servicios deben estar en el mismo servidor de Dokploy.")
    for name, default in (("BLOCIA_NETWORK_NAME", "blocia-production"), ("BLOCIA_SERVICE_NAMESPACE", "blocia-prod")):
        values = {environment_value(snapshot["env"], name, default) for snapshot in snapshots.values()}
        if len(values) != 1:
            raise DeploymentError(f"{name} debe coincidir en los tres servicios.")
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", next(iter(values))):
            raise DeploymentError(f"{name} debe usar letras, números, puntos, guiones o guiones bajos, sin espacios.")
    tokens = [environment_value(snapshots[service]["env"], "BLOCIA_INFERENCE_TOKEN") for service in ("inference", "api")]
    if not tokens[0] or tokens[0] != tokens[1]:
        raise DeploymentError("BLOCIA_INFERENCE_TOKEN debe estar configurado con el mismo valor en API e IA.")
    deadline = clock() + plan.services[0].timeout
    report["services"] = {}
    for config in plan.services:
        remaining = deadline - clock()
        if remaining <= 0:
            raise DeploymentError("Se agotó el tiempo de despliegue de los servicios.")
        report["services"][config.service] = "deploying"
        deploy(replace(config, timeout=remaining), compose_files[config.service], clients[config.service],
               current=snapshots[config.service], verify_release=False, clock=clock, sleep=sleep)
        report["services"][config.service] = "deployed"
    # Public readiness is checked after frontend exists, including the IA release.
    seen_running = set()
    started_waiting = clock()
    while clock() < deadline:
        states = {service: client.compose().get("composeStatus") for service, client in clients.items()}
        seen_running.update(service for service, status in states.items() if status == "running")
        failures = [service for service, status in states.items() if status == "error"
                    and (service in seen_running or clock() - started_waiting >= 30)]
        if failures:
            raise DeploymentError(f"Dokploy informó un error en {failures[0]}. Consultá sus registros; los volúmenes se conservaron.")
        if all(status == "done" for status in states.values()) and clients["frontend"].release_ready():
            report["services"] = {service: "ready" for service in SERVICES}
            return
        sleep(10)
    raise DeploymentError("Se agotó el tiempo esperando el mismo SHA y la IA lista en los tres servicios.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--services-directory", type=Path, default=Path(__file__).resolve().parents[1] / "deploy")
    parser.add_argument("--report", type=Path, default=Path("deployment-report.json"))
    args = parser.parse_args()
    report = {"status": "failed", "time": datetime.now(timezone.utc).isoformat()}
    try:
        plan = DeploymentPlan.from_environment()
        config = plan.services[0]
        report["release"] = config.release
        files = {service: (args.services_directory / service / "compose.yaml").read_text(encoding="utf-8") for service in SERVICES}
        clients = {item.service: DokployClient(item) for item in plan.services}
        deploy_services(plan, files, clients, report)
        report["status"] = "success"
        print(f"Despliegue verificado: {config.release}")
        return 0
    except DeploymentError as error:
        report["message"] = str(error)
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        report["message"] = "Error inesperado; consultá los registros de Dokploy."
        print(report["message"], file=sys.stderr)
        return 1
    finally:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
