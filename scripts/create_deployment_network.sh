#!/bin/sh
set -eu

if [ "$#" -gt 1 ]; then
    echo "Usage: sh scripts/create_deployment_network.sh [network-name]" >&2
    exit 1
fi

network_name="${1:-${BLOCIA_NETWORK_NAME:-blocia-production}}"
case "$network_name" in
    bridge|host|none|*[!a-zA-Z0-9_.-]*)
        echo "Choose a custom Docker network name using letters, numbers, dots, underscores or hyphens." >&2
        exit 1
        ;;
esac
case "$network_name" in
    [a-zA-Z0-9]*) ;;
    *) echo "The network name must begin with a letter or number." >&2; exit 1 ;;
esac

if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required on the Dokploy server." >&2
    exit 1
fi
if ! docker info --format '{{.ServerVersion}}' >/dev/null; then
    echo "Cannot access the Docker engine on this server." >&2
    exit 1
fi

network_matches() {
    network_configuration="$(docker network inspect --format '{{.Driver}} {{.Scope}} {{.Internal}}' "$network_name" 2>/dev/null)" || return 1
    [ "$network_configuration" = "bridge local false" ]
}

if docker network inspect "$network_name" >/dev/null 2>&1; then
    if ! network_matches; then
        echo "The existing network must be a local bridge with outgoing internet access. It was left unchanged." >&2
        exit 1
    fi
    printf 'Using existing network: %s\n' "$network_name"
    exit 0
fi

# No service, volume or existing network is removed or recreated.
if ! docker network create --driver bridge "$network_name" >/dev/null 2>&1; then
    # Another setup process may have created the same network in the meantime.
    if network_matches; then
        printf 'Using existing network: %s\n' "$network_name"
        exit 0
    fi
    echo "Could not create the deployment network." >&2
    exit 1
fi
if ! network_matches; then
    echo "The created network could not be verified." >&2
    exit 1
fi
printf 'Created network: %s\n' "$network_name"
