import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


path = Path(__file__).resolve().parents[3] / "scripts/deploy_dokploy.py"
spec = importlib.util.spec_from_file_location("deploy_dokploy", path)
deployment = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = deployment
spec.loader.exec_module(deployment)


def config():
    return deployment.Configuration("https://dokploy.example.com", "dedicated-id", "private-key", "a" * 40,
                                    "ghcr.io/owner/blocia", "https://app.example.com/api/ready",
                                    "https://app.example.com/version.json", 60)


def test_environment_preserves_credentials_and_unrelated_lines():
    existing = '# keep\r\nTOKEN="secret-value"\r\nRELEASE_TAG=old\r\nexport RELEASE_TAG=duplicate\r\nCUSTOM=unchanged'
    updated = deployment.update_environment(existing, config().release, config().image_prefix)
    assert '# keep\r\nTOKEN="secret-value"\r\n' in updated
    assert 'CUSTOM=unchanged\n' in updated
    assert updated.count("RELEASE_TAG=") == 1
    assert f"GHCR_IMAGE_PREFIX={config().image_prefix}\n" in updated


def test_multiline_values_are_preserved_without_replacing_their_contents():
    existing = 'PRIVATE_KEY="first-line\nRELEASE_TAG=part-of-private-value\nlast-line"\nRELEASE_TAG=old\n'
    updated = deployment.update_environment(existing, config().release, config().image_prefix)
    assert 'PRIVATE_KEY="first-line\nRELEASE_TAG=part-of-private-value\nlast-line"\n' in updated
    assert f"RELEASE_TAG={config().release}\n" in updated


@pytest.mark.parametrize("response", [b'true', b'null', b'', b'{"success":true}'])
def test_successful_write_acknowledgements_work_for_cloud_and_self_hosted(response):
    from io import BytesIO
    class Opener:
        def open(self, request, timeout):
            return BytesIO(response)
    client = deployment.DokployClient(config(), Opener())
    client.start()


class FakeClient:
    def __init__(self, *, target=True, ready_after=2):
        self.target = target
        self.updated = None
        self.started = False
        self.checks = 0
        self.ready_after = ready_after

    def compose(self):
        return {"sourceType": "raw", "composeType": "docker-compose", "composeStatus": "done",
                "composeFile": "x-blocia-deployment: 1\n" if self.target else "services: {}",
                "env": "TOKEN=private-secret\nCUSTOM=keep\nRELEASE_TAG=old\n"}

    def update(self, body):
        self.updated = body

    def start(self):
        self.started = True

    def release_ready(self):
        self.checks += 1
        return self.checks >= self.ready_after


def test_deploy_preserves_secrets_and_waits_for_new_release():
    client = FakeClient()
    ticks = SimpleNamespace(now=0)
    deployment.deploy(config(), "x-blocia-deployment: 1\nservices: {}", client,
                      clock=lambda: ticks.now, sleep=lambda seconds: setattr(ticks, "now", ticks.now + seconds))
    assert client.started
    assert client.checks == 2
    assert "TOKEN=private-secret\nCUSTOM=keep\n" in client.updated["env"]
    assert client.updated["autoDeploy"] is False
    assert set(client.updated) == {"composeId", "composeFile", "env", "autoDeploy"}


def test_wrong_compose_id_is_rejected_without_mutation():
    client = FakeClient(target=False)
    with pytest.raises(deployment.DeploymentError, match="composeId"):
        deployment.deploy(config(), "x-blocia-deployment: 1\n", client)
    assert client.updated is None
    assert not client.started


def test_old_deployment_never_counts_as_success():
    client = FakeClient(ready_after=100)
    ticks = SimpleNamespace(now=0)
    with pytest.raises(deployment.DeploymentError, match="agotó"):
        deployment.deploy(config(), "x-blocia-deployment: 1\n", client, clock=lambda: ticks.now,
                          sleep=lambda seconds: setattr(ticks, "now", ticks.now + seconds))


def test_api_key_is_not_sent_to_public_probes_and_volumes_are_kept():
    calls = []
    client = deployment.DokployClient(config())
    def request(url, **kwargs):
        calls.append((url, kwargs))
        if url == config().health_url:
            return {"ready": True, "release": config().release}
        if url == config().version_url:
            return {"release": config().release}
        return {}
    client.json_request = request
    client.start()
    assert calls[0][1]["body"]["freshVolumes"] is False
    assert client.release_ready()
    assert all(not kwargs.get("authenticated", False) for _, kwargs in calls[1:])


def test_public_probes_require_both_release_identifiers():
    client = deployment.DokployClient(config())
    client.json_request = lambda url, **kwargs: {"ready": True, "release": config().release if url == config().health_url else "old"}
    assert not client.release_ready()


def test_config_rejects_invalid_release_and_plain_http():
    env = {"DOKPLOY_URL": "https://dokploy.example.com", "DOKPLOY_COMPOSE_ID": "id", "DOKPLOY_API_KEY": "secret",
           "RELEASE_TAG": "a" * 40, "GHCR_IMAGE_PREFIX": "ghcr.io/owner/blocia",
           "PUBLIC_HEALTH_URL": "https://app.example.com/api/ready", "FRONTEND_VERSION_URL": "https://app.example.com/version.json"}
    assert deployment.Configuration.from_environment(env).release == "a" * 40
    for name, value in [("RELEASE_TAG", "main"), ("DOKPLOY_URL", "http://dokploy.example.com"),
                        ("FRONTEND_VERSION_URL", "https://other.example.com/version.json")]:
        with pytest.raises(deployment.DeploymentError):
            deployment.Configuration.from_environment({**env, name: value})


def service_config(service):
    return deployment.replace(config(), compose_id=f"{service}-id", service=service)


class ServiceClient(FakeClient):
    def __init__(self, service, events, *, wrong_role=False, token="shared-secret", network="blocia-production"):
        super().__init__(ready_after=1)
        self.service = service
        self.events = events
        self.wrong_role = wrong_role
        self.token = token
        self.network = network

    def compose(self):
        result = super().compose()
        role = "wrong" if self.wrong_role else self.service
        result["composeFile"] += f"x-blocia-service: {role}\n"
        result["env"] += f"BLOCIA_INFERENCE_TOKEN={self.token}\nBLOCIA_NETWORK_NAME={self.network}\n"
        result["serverId"] = "same-server"
        return result

    def start(self):
        self.events.append(self.service)
        super().start()


def plan_and_files():
    plan = deployment.DeploymentPlan(tuple(service_config(service) for service in deployment.SERVICES))
    files = {service: f"x-blocia-deployment: 1\nx-blocia-service: {service}\nservices: {{}}" for service in deployment.SERVICES}
    return plan, files


def test_three_resources_deploy_in_dependency_order_with_separate_environments():
    events = []
    plan, files = plan_and_files()
    clients = {service: ServiceClient(service, events) for service in deployment.SERVICES}
    report = {}
    deployment.deploy_services(plan, files, clients, report)
    assert events == ["inference", "api", "frontend"]
    assert report["services"] == {service: "ready" for service in deployment.SERVICES}
    assert [client.updated["composeId"] for client in clients.values()] == [f"{service}-id" for service in deployment.SERVICES]
    assert all("TOKEN=private-secret" in client.updated["env"] for client in clients.values())


@pytest.mark.parametrize("problem", ["wrong_role", "network", "token"])
def test_all_three_resources_are_checked_before_any_update(problem):
    events = []
    plan, files = plan_and_files()
    clients = {service: ServiceClient(service, events) for service in deployment.SERVICES}
    if problem == "wrong_role":
        clients["frontend"].wrong_role = True
    elif problem == "network":
        clients["frontend"].network = "different-network"
    else:
        clients["api"].token = "different-token"
    with pytest.raises(deployment.DeploymentError):
        deployment.deploy_services(plan, files, clients, {})
    assert not events
    assert all(client.updated is None for client in clients.values())


def test_services_on_different_servers_are_rejected_before_mutation():
    events = []
    plan, files = plan_and_files()
    clients = {service: ServiceClient(service, events) for service in deployment.SERVICES}
    original = clients["frontend"].compose
    clients["frontend"].compose = lambda: {**original(), "serverId": "other-server"}
    with pytest.raises(deployment.DeploymentError, match="mismo servidor"):
        deployment.deploy_services(plan, files, clients, {})
    assert not events


def test_new_ids_are_required_and_cannot_point_to_one_resource():
    env = {"DOKPLOY_URL": "https://dokploy.example.com", "DOKPLOY_API_KEY": "secret", "RELEASE_TAG": "a" * 40,
           "GHCR_IMAGE_PREFIX": "ghcr.io/owner/blocia", "PUBLIC_HEALTH_URL": "https://app.example.com/api/ready",
           "FRONTEND_VERSION_URL": "https://app.example.com/version.json"}
    with pytest.raises(deployment.DeploymentError, match="DOKPLOY_INFERENCE_COMPOSE_ID"):
        deployment.DeploymentPlan.from_environment(env)
    for service in deployment.SERVICES:
        env[f"DOKPLOY_{service.upper()}_COMPOSE_ID"] = "one-id"
    with pytest.raises(deployment.DeploymentError, match="diferente"):
        deployment.DeploymentPlan.from_environment(env)
    for service in deployment.SERVICES:
        env[f"DOKPLOY_{service.upper()}_COMPOSE_ID"] = f"{service}-id"
    assert [config.service for config in deployment.DeploymentPlan.from_environment(env).services] == list(deployment.SERVICES)


def test_split_readiness_requires_the_inference_release_too():
    client = deployment.DokployClient(service_config("frontend"))
    state = {"ready": True, "release": config().release, "inferenceRelease": "old"}
    client.json_request = lambda url, **kwargs: state if url == config().health_url else {"release": config().release}
    assert not client.release_ready()
    state["inferenceRelease"] = config().release
    assert client.release_ready()


def test_shared_settings_are_not_read_from_inside_multiline_credentials():
    environment = 'KEY="first\nBLOCIA_NETWORK_NAME=inside-secret\nlast"\nBLOCIA_NETWORK_NAME="actual-network" # comment\n'
    assert deployment.environment_value(environment, "BLOCIA_NETWORK_NAME") == "actual-network"
