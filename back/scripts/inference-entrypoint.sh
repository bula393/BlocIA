#!/bin/sh
set -eu

case "${BLOCIA_ENABLE_LOCAL_CHAT:-0}" in
    0|1) ;;
    *) echo "BLOCIA_ENABLE_LOCAL_CHAT must be 0 or 1." >&2; exit 1 ;;
esac
case "${BLOCIA_PREPARE_MODELS:-1}" in
    0|1) ;;
    *) echo "BLOCIA_PREPARE_MODELS must be 0 or 1." >&2; exit 1 ;;
esac

if [ "${ENVIRONMENT:-production}" = "production" ] && [ -z "${BLOCIA_INFERENCE_TOKEN:-}" ]; then
    echo "BLOCIA_INFERENCE_TOKEN is required in production." >&2
    exit 1
fi

if [ "${BLOCIA_PREPARE_MODELS:-1}" = "1" ]; then
    # Preparation verifies the pinned manifest and skips complete existing models.
    if [ "${BLOCIA_ENABLE_LOCAL_CHAT:-0}" = "1" ]; then
        python -m ml.prepare
    else
        python -m ml.prepare --classifier-only
    fi
fi

export BLOCIA_PRELOAD_LOCAL_CHAT="${BLOCIA_ENABLE_LOCAL_CHAT:-0}"
exec "$@"
