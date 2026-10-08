import importlib.util
from pathlib import Path
import sys

import pytest


path = Path(__file__).resolve().parents[3] / "scripts/deploy_dokploy_applications.py"
spec = importlib.util.spec_from_file_location("deploy_dokploy_applications", path)
deployment = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = deployment
spec.loader.exec_module(deployment)


def environment():
    return {
        "DOKPLOY_URL": "https://dokploy.example.com",
        "DOKPLOY_API_KEY": "private-api-key",
        "DOKPLOY_CLASIFICADOR_APPLICATION_ID": "classificador-id",
        "DOKPLOY_BACK_APPLICATION_ID": "back-id",
        "DOKPLOY_FRONT_APPLICATION_ID": "front-id",
        "GHCR_IMAGE_PREFIX": "ghcr.io/owner/blocia",
        "RELEASE_TAG": "a" * 40,
    }


def test_configuration_maps_three_distinct_applications():
    config = deployment.Configuration.from_environment(environment())
    assert config.application_ids == {
        "inference": "classificador-id",
        "api": "back-id",
        "frontend": "front-id",
    }


@pytest.mark.parametrize("name,value", [
    ("DOKPLOY_URL", "http://dokploy.example.com"),
    ("DOKPLOY_URL", "https://dokploy.example.com/api"),
    ("RELEASE_TAG", "main"),
    ("GHCR_IMAGE_PREFIX", "docker.io/owner/blocia"),
    ("DOKPLOY_BACK_APPLICATION_ID", "bad id"),
])
def test_configuration_rejects_invalid_values(name, value):
    with pytest.raises(deployment.DeploymentError):
        deployment.Configuration.from_environment({**environment(), name: value})


def test_application_ids_must_be_unique():
    env = environment()
    env["DOKPLOY_BACK_APPLICATION_ID"] = env["DOKPLOY_FRONT_APPLICATION_ID"]
    with pytest.raises(deployment.DeploymentError, match="diferente"):
        deployment.Configuration.from_environment(env)


def test_registry_token_requires_a_username():
    with pytest.raises(deployment.DeploymentError, match="GHCR_USERNAME"):
        deployment.Configuration.from_environment({**environment(), "GHCR_READ_TOKEN": "read-token"})


def test_public_registry_needs_no_password_and_private_credentials_are_supported():
    public = deployment.Configuration.from_environment(environment())
    private = deployment.Configuration.from_environment({
        **environment(), "GHCR_USERNAME": "github-user", "GHCR_READ_TOKEN": "read-token",
    })
    assert public.registry_username is None
    assert public.registry_password is None
    assert private.registry_username == "github-user"
    assert private.registry_password == "read-token"


def test_client_uses_dokploy_api_for_image_and_application_deployment():
    from io import BytesIO

    requests = []

    class Opener:
        def open(self, request, timeout):
            requests.append((request, timeout))
            return BytesIO(b"{}")

    config = deployment.Configuration.from_environment(environment())
    client = deployment.DokployClient(config, Opener())
    client.save_docker_provider(application_id="back-id", image="ghcr.io/owner/blocia-api:" + "a" * 40)
    client.deploy_application(application_id="back-id", label="back")

    assert [request.full_url for request, _ in requests] == [
        "https://dokploy.example.com/api/application.saveDockerProvider",
        "https://dokploy.example.com/api/application.deploy",
    ]
    assert all(request.get_header("X-api-key") == "private-api-key" for request, _ in requests)
    assert requests[0][0].data == (
        b'{"applicationId": "back-id", "dockerImage": "ghcr.io/owner/blocia-api:'
        + ("a" * 40).encode()
        + b'", "registryUrl": "ghcr.io", "username": null, "password": null}'
    )
    assert b"private-api-key" not in requests[0][0].data
    assert requests[1][0].data.startswith(b'{"applicationId": "back-id", "title": "BlocIA aaaaaaaaaaaa"')


def test_images_are_updated_before_deployments_in_dependency_order():
    events = []
    config = deployment.Configuration.from_environment(environment())

    class Client:
        def save_docker_provider(self, *, application_id, image):
            events.append(("save", application_id, image))

        def deploy_application(self, *, application_id, label):
            events.append(("deploy", application_id, label))

    report = {}
    deployment.deploy_applications(config, Client(), report)

    assert [event[0] for event in events] == ["save", "save", "save", "deploy", "deploy", "deploy"]
    assert [event[2] for event in events[:3]] == [
        f"ghcr.io/owner/blocia-inference:{'a' * 40}",
        f"ghcr.io/owner/blocia-api:{'a' * 40}",
        f"ghcr.io/owner/blocia-frontend:{'a' * 40}",
    ]
    assert [event[2] for event in events[3:]] == ["clasificador", "back", "front"]
    assert report["services"] == {
        "clasificador": {"image": f"ghcr.io/owner/blocia-inference:{'a' * 40}", "status": "deployment_requested"},
        "back": {"image": f"ghcr.io/owner/blocia-api:{'a' * 40}", "status": "deployment_requested"},
        "front": {"image": f"ghcr.io/owner/blocia-frontend:{'a' * 40}", "status": "deployment_requested"},
    }


def test_provider_update_failure_prevents_any_deployment():
    config = deployment.Configuration.from_environment(environment())

    class Client:
        def __init__(self):
            self.deployed = []

        def save_docker_provider(self, *, application_id, image):
            if application_id == "back-id":
                raise deployment.DeploymentError("Dokploy rejected the update")

        def deploy_application(self, *, application_id, label):
            self.deployed.append(application_id)

    client = Client()
    with pytest.raises(deployment.DeploymentError):
        deployment.deploy_applications(config, client, {})
    assert client.deployed == []
