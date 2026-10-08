"""Check the Compose, Docker and GitHub Actions contracts without deploying."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_mapping(path: str) -> dict:
    # BaseLoader preserves Actions' `on` key instead of YAML 1.1's boolean `on`.
    data = yaml.load((ROOT / path).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    require(isinstance(data, dict), f"{path}: expected a YAML mapping")
    return data


def validate_release_image(image: str, service: str, label: str) -> None:
    pattern = rf"\$\{{GHCR_IMAGE_PREFIX(?::\?[^}}]+)?\}}-{service}:\$\{{RELEASE_TAG(?::\?[^}}]+)?\}}"
    require(bool(re.fullmatch(pattern, image)), f"{label}: image must use the verified release tag")


def validate_separate_service(compose: dict, service: str) -> str:
    label = f"Dokploy {service}"
    require(compose.get("x-blocia-deployment") == "1", f"{label}: deployment marker is required")
    require(compose.get("x-blocia-service") == service, f"{label}: service marker must match its role")
    services = compose.get("services", {})
    require(set(services) == {service}, f"{label}: exactly one service with the matching role is required")
    definition = services[service]
    require("depends_on" not in definition, f"{label}: dependencies cannot cross separate Compose resources")
    validate_release_image(definition.get("image", ""), service, label)

    networks = compose.get("networks", {})
    application = networks.get("application", {})
    require(application.get("external") == "true", f"{label}: application network must be external")
    network_name = application.get("name", "")
    require(bool(network_name), f"{label}: application network needs a shared explicit name")
    membership = set(definition.get("networks", []))
    require("application" in membership, f"{label}: service must join the application network")
    if service in {"api", "inference"}:
        require("ports" not in definition, f"{label}: backend services must not publish host ports")
        require(membership == {"application"}, f"{label}: backend services must remain on the private application network")
        release = definition.get("environment", {}).get("RELEASE_TAG", "")
        require(bool(re.fullmatch(r"\$\{RELEASE_TAG(?::\?[^}]+)?\}", release)), f"{label}: runtime release must match its image tag")
        declared_volumes = compose.get("volumes", {})
        storage_path = "/app/data" if service == "api" else "/app/models"
        mounts = [
            (mount.get("source", ""), mount.get("target", "")) if isinstance(mount, dict)
            else tuple(str(mount).split(":")[:2])
            for mount in definition.get("volumes", [])
        ]
        persistent_storage = any(len(mount) == 2 and mount[0] in declared_volumes and mount[1] == storage_path for mount in mounts)
        require(persistent_storage, f"{label}: a persistent named volume must be mounted at {storage_path}")
    else:
        require(networks.get("dokploy-network", {}).get("external") == "true", f"{label}: Dokploy routing network must be external")
        require(membership == {"application", "dokploy-network"}, f"{label}: frontend must join the application and routing networks")
    return network_name


def validate_compose() -> None:
    local = load_mapping("compose.yaml")
    production = load_mapping("deploy/dokploy.compose.yaml")
    dockerfile = (ROOT / "back/Dockerfile").read_text(encoding="utf-8")
    inference_stage = re.split(r"^FROM\s+.+\s+AS\s+inference\s*$", dockerfile, flags=re.I | re.M)
    inference_has_healthcheck = len(inference_stage) == 2 and "HEALTHCHECK" in inference_stage[1] and "/ready" in inference_stage[1]
    for label, compose in (("local", local), ("Dokploy", production)):
        services = compose.get("services", {})
        require(all(name in services for name in ("frontend", "api", "inference")), f"{label}: missing one of the three services")
        require("ports" not in services["inference"], f"{label}: inference must remain on the private Docker network")
        require("healthcheck" in services["inference"] or inference_has_healthcheck, f"{label}: inference readiness check is required")
        require(bool(compose.get("volumes")), f"{label}: persistent volumes are required")
    for service in ("frontend", "api", "inference"):
        image = production["services"][service].get("image", "")
        validate_release_image(image, service, f"all-in-one Dokploy {service}")
    separate_networks = {
        validate_separate_service(load_mapping(f"deploy/{service}/compose.yaml"), service)
        for service in ("inference", "api", "frontend")
    }
    require(len(separate_networks) == 1, "separate Dokploy resources must share the same external application network name")
    for target in ("api", "inference"):
        require(bool(re.search(rf"^FROM\s+.+\s+AS\s+{target}\s*$", dockerfile, re.I | re.M)), f"backend Dockerfile: missing {target} target")
    frontend = (ROOT / "front/Dockerfile").read_text(encoding="utf-8")
    require("RELEASE_TAG" in frontend and "version.json" in frontend, "frontend container must expose its immutable release version")


def validate_workflows() -> None:
    ci = load_mapping(".github/workflows/ci.yml")
    deploy = load_mapping(".github/workflows/deploy.yml")
    require(ci.get("name") == "CI", "CI workflow name must match the deployment workflow_run trigger")
    require(all(event in ci.get("on", {}) for event in ("push", "pull_request", "workflow_call")), "CI must support pushes, pull requests and manual deployment verification")
    backend_steps = ci.get("jobs", {}).get("backend", {}).get("steps", [])
    require(any(step.get("run") == "mkdir -p ../test-results" for step in backend_steps), "backend CI must create the JUnit artifact directory before pytest")
    require("pull_request" not in deploy.get("on", {}) and "pull_request_target" not in deploy.get("on", {}), "deployment must never run on pull requests")
    require(deploy.get("on", {}).get("workflow_run", {}).get("workflows") == ["CI"], "deployment must wait for CI completion")
    jobs = deploy.get("jobs", {})
    eligibility = jobs.get("eligible", {}).get("if", "")
    for check in ("conclusion == 'success'", "workflow_run.event == 'push'", "head_repository.full_name == github.repository", "vars.DEPLOY_BRANCH || 'main'"):
        require(check in eligibility, f"release eligibility is missing: {check}")
    require("DEPLOY_ENABLED" not in eligibility, "image publication must not depend on Dokploy deployment settings")
    require(jobs.get("verify-manual", {}).get("uses") == "./.github/workflows/ci.yml", "manual deployments must run the same CI workflow")
    publish = jobs.get("publish", {})
    require(set(publish.get("needs", [])) == {"eligible", "verify-manual"}, "publishing must depend on release eligibility and manual verification")
    require("needs.verify-manual.result == 'success'" in publish.get("if", ""), "manual publish must require successful verification")
    require("needs.eligible.outputs.sha" in str(publish), "published images must be pinned to the verified commit")
    require("needs.eligible.outputs.current == 'true'" in publish.get("if", ""), "publishing must skip a release when the deployment branch has advanced")
    require(publish.get("permissions", {}).get("packages") == "write", "only publishing requires registry write access")
    for name, job in jobs.items():
        if name != "publish":
            require(job.get("permissions", {}).get("packages") != "write", f"{name}: registry write permission is unnecessary")
    deployment = jobs.get("deploy", {})
    require(set(deployment.get("needs", [])) == {"eligible", "publish"}, "production deployment must wait for all three images")
    require(deployment.get("if") == "vars.DEPLOY_ENABLED == 'true'", "Dokploy deployment must remain disabled until explicitly configured")
    require(deployment.get("environment", {}).get("name") == "production", "production deployment must use its GitHub environment")
    require(int(deployment.get("timeout-minutes", "0")) >= 50, "sequential service deployment needs at least 50 minutes")
    steps = deployment.get("steps", [])
    invocation = next((step for step in steps if step.get("run") == "python scripts/deploy_dokploy.py"), {})
    require(invocation.get("if") == "steps.branch.outputs.current == 'true'", "production deployment must recheck the branch after the image builds")
    branch_check = next((step for step in steps if step.get("id") == "branch"), {})
    require("gh api --method GET" in branch_check.get("run", "") and '"$latest_sha" == "$COMMIT_SHA"' in branch_check.get("run", ""), "deployment must compare the current branch head against the verified release")
    required_env = {"DOKPLOY_URL", "DOKPLOY_INFERENCE_COMPOSE_ID", "DOKPLOY_API_COMPOSE_ID", "DOKPLOY_FRONTEND_COMPOSE_ID", "DOKPLOY_API_KEY", "RELEASE_TAG", "GHCR_IMAGE_PREFIX", "PUBLIC_HEALTH_URL", "FRONTEND_VERSION_URL"}
    require(required_env <= invocation.get("env", {}).keys(), "Dokploy deployment is missing required configuration")
    require("DOKPLOY_COMPOSE_ID" not in invocation.get("env", {}), "default deployment must use three separate Compose resources")
    ci_container_steps = ci.get("jobs", {}).get("containers", {}).get("steps", [])
    compose_checks = "\n".join(step.get("run", "") for step in ci_container_steps)
    for service in ("inference", "api", "frontend"):
        require(f"docker compose -f deploy/{service}/compose.yaml config --quiet" in compose_checks, f"CI must validate the separate {service} Compose resource")


def main() -> int:
    try:
        validate_compose()
        validate_workflows()
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Deployment validation failed: {error}")
        return 1
    print("Compose, Docker targets and deployment workflow contracts are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
