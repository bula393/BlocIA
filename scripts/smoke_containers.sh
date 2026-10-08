#!/usr/bin/env bash
set -euo pipefail

smoke_prefix="${BLOCIA_SMOKE_PREFIX:-blocia-ci}"
smoke_network="$smoke_prefix"
frontend_container="$smoke_prefix-frontend"
api_container="$smoke_prefix-api"
ip_holder_container="$smoke_prefix-ip-holder"
smoke_port="${BLOCIA_SMOKE_PORT:-8080}"
smoke_url="http://127.0.0.1:$smoke_port"
smoke_python="${BLOCIA_SMOKE_PYTHON:-python}"

is_owned() {
  local resource_type="$1"
  local resource_name="$2"
  local label_template='{{index .Config.Labels "io.blocia.smoke"}}'
  if [[ "$resource_type" == network ]]; then
    label_template='{{index .Labels "io.blocia.smoke"}}'
  fi
  local marker
  marker="$(docker "$resource_type" inspect --format "$label_template" "$resource_name" 2> /dev/null || true)"
  [[ "${marker%$'\r'}" == "$smoke_prefix" ]]
}

cleanup() {
  for container in "$frontend_container" "$api_container" "$ip_holder_container"; do
    if is_owned container "$container"; then
      docker rm --force "$container" > /dev/null 2>&1 || true
    fi
  done
  if is_owned network "$smoke_network"; then
    docker network rm "$smoke_network" > /dev/null 2>&1 || true
  fi
}

if [[ "${1:-}" == "--cleanup" ]]; then
  cleanup
  exit 0
fi

: "${RELEASE_TAG:?RELEASE_TAG is required}"
: "${ACCESS_TOKEN_SECRET:?ACCESS_TOKEN_SECRET is required}"
: "${BLOCIA_INFERENCE_TOKEN:?BLOCIA_INFERENCE_TOKEN is required}"
frontend_image="${BLOCIA_SMOKE_FRONTEND_IMAGE:-blocia-ci-frontend:$RELEASE_TAG}"
api_image="${BLOCIA_SMOKE_API_IMAGE:-blocia-ci-api:$RELEASE_TAG}"

finish() {
  smoke_exit=$?
  if [[ "$smoke_exit" != 0 ]]; then
    for container in "$api_container" "$frontend_container"; do
      if is_owned container "$container"; then
        docker logs --tail 100 "$container" 2>&1 || true
      fi
    done
  fi
  cleanup
  exit "$smoke_exit"
}

start_api() {
  docker run --detach --name "$api_container" --network "$smoke_network" --network-alias api \
    --label "io.blocia.smoke=$smoke_prefix" \
    --env ENVIRONMENT=development --env ACCESS_TOKEN_SECRET --env RELEASE_TAG \
    --env BLOCIA_INFERENCE_TOKEN --env BLOCIA_INFERENCE_URL=http://inference:8001 \
    --env BLOCIA_PRELOAD_CLASSIFIER=0 --env BLOCIA_PRELOAD_LOCAL_CHAT=0 \
    "$api_image" > /dev/null
}

frontend_ready() {
  curl --fail --silent --max-time 15 "$smoke_url/healthz" > /dev/null &&
    curl --fail --silent --max-time 15 "$smoke_url/version.json" |
      release_matches
}

stack_ready() {
  frontend_ready && curl --fail --silent --max-time 15 "$smoke_url/api/health" |
    release_matches
}

release_matches() {
  "$smoke_python" -c '
import json, sys
try:
    matches = json.load(sys.stdin).get("release") == sys.argv[1]
except (ValueError, AttributeError):
    matches = False
sys.exit(0 if matches else 1)
' "$RELEASE_TAG"
}

container_ip() {
  docker inspect "$1" | "$smoke_python" -c \
    'import json, sys; address = json.load(sys.stdin)[0]["NetworkSettings"]["Networks"][sys.argv[1]]["IPAddress"]; assert address; sys.stdout.write(address)' \
    "$smoke_network"
}

wait_for() {
  local probe="$1"
  local failure_message="$2"
  for attempt in {1..30}; do
    if "$probe"; then
      return 0
    fi
    sleep 2
  done
  printf '%s\n' "$failure_message" >&2
  return 1
}

for container in "$frontend_container" "$api_container" "$ip_holder_container"; do
  if docker container inspect "$container" > /dev/null 2>&1; then
    printf 'Smoke test container name is already in use: %s\n' "$container" >&2
    exit 1
  fi
done
if docker network inspect "$smoke_network" > /dev/null 2>&1; then
  printf 'Smoke test network name is already in use: %s\n' "$smoke_network" >&2
  exit 1
fi
trap finish EXIT

# An explicit subnet lets the holder reserve the old address after API removal.
docker network create --subnet "${BLOCIA_SMOKE_SUBNET:-172.30.249.0/24}" \
  --label "io.blocia.smoke=$smoke_prefix" "$smoke_network" > /dev/null
docker run --detach --name "$frontend_container" --network "$smoke_network" \
  --label "io.blocia.smoke=$smoke_prefix" \
  --publish "127.0.0.1:$smoke_port:8080" --env BLOCIA_API_UPSTREAM=api:8000 \
  "$frontend_image" > /dev/null
wait_for frontend_ready 'Frontend failed to start before the API was available.'
printf 'Frontend starts while the API is absent.\n'

start_api
wait_for stack_ready 'Frontend failed to proxy the first API container.'
old_ip="$(container_ip "$api_container")"
docker rm --force "$api_container" > /dev/null
docker run --detach --name "$ip_holder_container" --network "$smoke_network" --ip "$old_ip" \
  --label "io.blocia.smoke=$smoke_prefix" \
  --entrypoint /bin/sh "$frontend_image" -c 'sleep 60' > /dev/null
start_api
new_ip="$(container_ip "$api_container")"
if [[ "$old_ip" == "$new_ip" ]]; then
  printf 'API recreation did not change its IP address.\n' >&2
  exit 1
fi
wait_for stack_ready 'Frontend failed to recover after the API changed its IP address.'
printf 'Frontend recovers after an API deployment changes its IP address.\n'
