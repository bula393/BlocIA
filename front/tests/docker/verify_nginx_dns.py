"""Exercise the actual Nginx proxy against a separately recreated Docker API.

Run after building the frontend and API images. No models, database or external
server are needed. Only uniquely named temporary Docker resources are removed.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid


FRONT = Path(__file__).resolve().parents[2]
BACKEND = '''from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class Handler(BaseHTTPRequestHandler):
    def respond(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        result = {
            "identity": os.environ["STUB_IDENTITY"],
            "path": self.path,
            "body": body.decode(),
            "headers": {key.lower(): value for key, value in self.headers.items()},
        }
        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = respond
    do_POST = respond

    def log_message(self, *args):
        pass

HTTPServer(("0.0.0.0", int(os.environ["PORT"])), Handler).serve_forever()
'''


def docker(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["docker", *args], capture_output=True, text=True, check=False
    )
    if check and result.returncode:
        raise RuntimeError(f"Docker {args[0]} failed: {result.stderr.strip()}")
    return (result.stdout or result.stderr).strip()


def request(base: str, path: str, *, body: bytes | None = None, headers=None):
    req = Request(base + path, data=body, headers=headers or {})
    try:
        with urlopen(req, timeout=12) as response:
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()


def wait_for(check, *, seconds: int = 20):
    deadline = time.monotonic() + seconds
    last_error = None
    while time.monotonic() < deadline:
        try:
            value = check()
            if value:
                return value
        except (URLError, TimeoutError, ConnectionError) as error:
            last_error = error
        time.sleep(0.5)
    raise AssertionError(f"Condition did not recover within {seconds}s: {last_error}")


def docker_directive(source: str, directive: str) -> str:
    lines = source.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(directive + " "))
    end = start
    while lines[end].endswith("\\"):
        end += 1
    return "\n".join(lines[start:end + 1]) + "\n"


def check_container_health(container: str) -> None:
    command = json.loads(docker("inspect", container))[0]["Config"]["Healthcheck"]["Test"]
    if command[0] == "CMD-SHELL":
        docker("exec", container, "/bin/sh", "-c", command[1])
    else:
        assert command[0] == "CMD"
        docker("exec", container, *command[1:])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend-image", default="blocia-frontend:codex-review")
    parser.add_argument("--api-image", default="blocia-api:codex-review")
    parser.add_argument("--frontend-port", type=int, default=8080)
    parser.add_argument("--api-port", type=int, default=8000)
    args = parser.parse_args()
    if not all(0 < port < 65536 for port in (args.frontend_port, args.api_port)):
        parser.error("Ports must be between 1 and 65535.")
    suffix = uuid.uuid4().hex[:12]
    network = f"blocia-nginx-smoke-{suffix}"
    frontend = f"{network}-front"
    api = f"{network}-api"
    alias = "blocia-prod-api"
    image = f"blocia-nginx-smoke:{suffix}"
    api_image = f"blocia-api-port-smoke:{suffix}"
    with tempfile.TemporaryDirectory(prefix="nginx-dns-", dir=FRONT / "tests" / "docker") as temporary:
        context = Path(temporary).resolve()
        # Keep temporary file creation and cleanup inside the workspace.
        context.relative_to(FRONT)
        (context / "default.conf.template").write_bytes(
            (FRONT / "nginx" / "default.conf.template").read_bytes()
        )
        (context / "backend.py").write_text(BACKEND, encoding="utf-8")
        frontend_source = (FRONT / "Dockerfile").read_text(encoding="utf-8")
        (context / "Dockerfile").write_text(
            f"FROM {args.frontend_image}\n"
            + docker_directive(frontend_source, "ENV")
            + "COPY default.conf.template /etc/nginx/templates/default.conf.template\n"
            + docker_directive(frontend_source, "HEALTHCHECK"),
            encoding="utf-8",
        )
        try:
            docker("build", "--pull=false", "--tag", image, str(context))
            print(docker("run", "--rm", "--entrypoint", "nginx", image, "-v"))
            docker("network", "create", network)
            subnet = json.loads(docker("network", "inspect", network))[0]["IPAM"]["Config"][0]["Subnet"]
            addresses = ipaddress.ip_network(subnet)
            first_ip, second_ip = str(addresses[10]), str(addresses[11])
            docker(
                "run", "--detach", "--name", frontend, "--network", network,
                "--publish", f"127.0.0.1::{args.frontend_port}", "--env",
                f"BLOCIA_API_UPSTREAM={alias}:{args.api_port}", "--env",
                f"PORT={args.frontend_port}", image,
            )
            port = docker("port", frontend, f"{args.frontend_port}/tcp").rsplit(":", 1)[1]
            base = f"http://127.0.0.1:{port}"
            wait_for(lambda: request(base, "/healthz")[0] == 200)
            check_container_health(frontend)
            assert request(base, "/api/ping")[0] == 502
            status, headers, content = request(base, "/auth/google/callback?code=example")
            assert status == 200 and "text/html" in headers["Content-Type"]
            assert b"<html" in content.lower()
            initial_start = docker("inspect", "--format", "{{.State.StartedAt}}", frontend)
            print("Frontend starts without the API; health and SPA callback remain available.")

            def start_api(identity: str, address: str) -> None:
                docker(
                    "run", "--detach", "--name", api, "--network", network,
                    "--network-alias", alias, "--ip", address, "--env",
                    f"STUB_IDENTITY={identity}", "--env", f"PORT={args.api_port}", "--mount",
                    f"type=bind,source={context},target=/smoke,readonly",
                    "--entrypoint", "python", args.api_image, "-u", "/smoke/backend.py",
                )

            def identity() -> str | None:
                status, _, body = request(base, "/api/ping")
                return json.loads(body)["identity"] if status == 200 else None

            start_api("first", first_ip)
            wait_for(lambda: identity() == "first")
            status, _, body = request(base, "/api/ping?source=prefix&value=a%2Fb")
            assert status == 200
            assert json.loads(body)["path"] == "/ping?source=prefix&value=a%2Fb"
            status, _, body = request(
                base, "/api/chat?mode=personal", body=b'{"message":"diagnostic"}',
                headers={"Content-Type": "application/json", "Host": "frontend.test",
                         "X-Forwarded-Proto": "https", "X-Forwarded-For": "192.0.2.40"},
            )
            result = json.loads(body)
            assert status == 200 and result["path"] == "/chat?mode=personal"
            assert result["body"] == '{"message":"diagnostic"}'
            assert result["headers"]["host"] == "frontend.test"
            assert result["headers"]["x-forwarded-host"] == "frontend.test"
            assert result["headers"]["x-forwarded-proto"] == "https"
            assert result["headers"]["x-forwarded-for"].startswith("192.0.2.40, ")
            for path in ("/profile/me?view=raw", "/usage/current", "/technical-profile/me"):
                status, _, body = request(base, path)
                assert status == 200 and json.loads(body)["path"] == path
            print("API prefix, query, POST body, forwarding headers and raw profile routes pass.")

            docker("rm", "--force", api)
            start_api("replacement", second_ip)
            wait_for(lambda: identity() == "replacement")
            assert docker("inspect", "--format", "{{.State.StartedAt}}", frontend) == initial_start
            print(f"API replacement {first_ip} -> {second_ip} resolves without restarting Nginx.")

            # Exercise the real Uvicorn command and both image healthchecks at
            # the requested ports, using already installed local image layers.
            docker("rm", "--force", api)
            backend_source = (FRONT.parent / "back" / "Dockerfile").read_text(encoding="utf-8")
            api_stage = re.split(r"^FROM\s+.+\s+AS\s+api\s*$", backend_source, flags=re.I | re.M)[1]
            api_stage = re.split(r"^FROM\s+", api_stage, maxsplit=1, flags=re.M)[0]
            (context / "Dockerfile.api").write_text(
                f"FROM {args.api_image}\n"
                + docker_directive(api_stage, "ENV")
                + docker_directive(api_stage, "HEALTHCHECK")
                + docker_directive(api_stage, "CMD"),
                encoding="utf-8",
            )
            docker("build", "--pull=false", "--file", str(context / "Dockerfile.api"), "--tag", api_image, str(context))
            docker(
                "run", "--detach", "--name", api, "--network", network,
                "--network-alias", alias, "--ip", second_ip,
                "--publish", f"127.0.0.1::{args.api_port}", "--env", f"PORT={args.api_port}",
                "--env", "ACCESS_TOKEN_SECRET=runtime-port-smoke-key-for-local-test-only",
                "--env", f"FRONTEND_URL=https://frontend.example.test:{args.frontend_port}",
                "--env", "BLOCIA_DATABASE_PATH=/tmp/port-smoke.sqlite3", api_image,
            )
            api_port = docker("port", api, f"{args.api_port}/tcp").rsplit(":", 1)[1]
            wait_for(lambda: request(f"http://127.0.0.1:{api_port}", "/health")[0] == 200)
            check_container_health(api)
            wait_for(lambda: request(base, "/api/health")[0] == 200)
            print(f"Real API, frontend proxy and both image healthchecks pass on internal ports {args.api_port}/{args.frontend_port}.")
        except Exception:
            print(docker("logs", "--tail", "30", api, check=False))
            raise
        finally:
            docker("rm", "--force", api, frontend, check=False)
            docker("network", "rm", network, check=False)
            docker("image", "rm", image, api_image, check=False)


if __name__ == "__main__":
    main()
