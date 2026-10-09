import importlib.util
from pathlib import Path

import pytest


path = Path(__file__).resolve().parents[3] / "scripts/validate_deployment.py"
spec = importlib.util.spec_from_file_location("validate_deployment", path)
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)


def test_repository_deployment_contracts_are_valid():
    validation.validate_compose()
    validation.validate_workflows()


def test_resources_with_different_network_names_are_rejected(monkeypatch):
    load_mapping = validation.load_mapping

    def mismatched_network(path):
        compose = load_mapping(path)
        if path == "deploy/api/compose.yaml":
            compose["networks"]["application"]["name"] = "disconnected-network"
        return compose

    monkeypatch.setattr(validation, "load_mapping", mismatched_network)
    with pytest.raises(ValueError, match="same external application network name"):
        validation.validate_compose()


@pytest.mark.parametrize("service", ["inference", "api", "frontend"])
def test_separate_resource_rejects_the_wrong_role(service):
    compose = validation.load_mapping(f"deploy/{service}/compose.yaml")
    compose["x-blocia-service"] = "other"
    with pytest.raises(ValueError, match="service marker"):
        validation.validate_separate_service(compose, service)


@pytest.mark.parametrize("service", ["inference", "api", "frontend"])
def test_separate_resource_rejects_multiple_services_and_cross_resource_dependencies(service):
    compose = validation.load_mapping(f"deploy/{service}/compose.yaml")
    compose["services"]["unexpected"] = {}
    with pytest.raises(ValueError, match="exactly one service"):
        validation.validate_separate_service(compose, service)
    del compose["services"]["unexpected"]
    compose["services"][service]["depends_on"] = ["other"]
    with pytest.raises(ValueError, match="dependencies cannot cross"):
        validation.validate_separate_service(compose, service)


@pytest.mark.parametrize("service", ["api", "inference"])
def test_backend_resources_reject_public_exposure_and_missing_persistence_config(service):
    compose = validation.load_mapping(f"deploy/{service}/compose.yaml")
    definition = compose["services"][service]
    definition["ports"] = ["8000:8000"]
    with pytest.raises(ValueError, match="host ports"):
        validation.validate_separate_service(compose, service)
    del definition["ports"]
    if service == "api":
        definition["environment"]["DATABASE_URL"] = ""
        message = "DATABASE_URL"
    else:
        definition["volumes"] = []
        message = "persistent named volume"
    with pytest.raises(ValueError, match=message):
        validation.validate_separate_service(compose, service)


@pytest.mark.parametrize("service", ["api", "inference"])
def test_runtime_version_cannot_disagree_with_the_published_image(service):
    compose = validation.load_mapping(f"deploy/{service}/compose.yaml")
    compose["services"][service]["environment"]["RELEASE_TAG"] = "old-release"
    with pytest.raises(ValueError, match="runtime release must match"):
        validation.validate_separate_service(compose, service)


@pytest.mark.parametrize("service", ["inference", "api", "frontend"])
def test_separate_resources_reject_mutable_release_tags_and_project_scoped_networks(service):
    compose = validation.load_mapping(f"deploy/{service}/compose.yaml")
    definition = compose["services"][service]
    pinned_image = definition["image"]
    definition["image"] = f"ghcr.io/owner/blocia-{service}:latest"
    with pytest.raises(ValueError, match="verified release tag"):
        validation.validate_separate_service(compose, service)
    definition["image"] = pinned_image
    compose["networks"]["application"]["external"] = "false"
    with pytest.raises(ValueError, match="network must be external"):
        validation.validate_separate_service(compose, service)
