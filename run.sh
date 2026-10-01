#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACK_DIR="$ROOT_DIR/back"
FRONT_DIR="$ROOT_DIR/front"
VENV_DIR="$BACK_DIR/.venv-linux"
RUNTIME_DIR="$BACK_DIR/data/run"
BACK_PID_FILE="$RUNTIME_DIR/backend.pid"
FRONT_PID_FILE="$RUNTIME_DIR/frontend.pid"
ACTION="${1:-start}"

umask 077

log() { printf '[BloqIA] %s\n' "$*"; }
fail() { printf '[BloqIA] Error: %s\n' "$*" >&2; exit 1; }

case "$ACTION" in
  start|restart|stop|status) ;;
  *) fail "Uso: ./run.sh [start|restart|stop|status]" ;;
esac

mkdir -p "$RUNTIME_DIR"
chmod 700 "$RUNTIME_DIR"

process_matches() {
  local pid_file="$1" expected="$2" pid command_line
  [[ -s "$pid_file" ]] || return 1
  read -r pid < "$pid_file" || return 1
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  [[ -r "/proc/$pid/cmdline" ]] || return 1
  command_line="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  [[ "$command_line" == *"$expected"* ]]
}

stop_service() {
  local name="$1" pid_file="$2" expected="$3" pid
  if process_matches "$pid_file" "$expected"; then
    read -r pid < "$pid_file"
    kill -TERM "$pid" 2>/dev/null || true
    for _ in {1..50}; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.1
    done
    if kill -0 "$pid" 2>/dev/null; then
      kill -KILL "$pid" 2>/dev/null || true
    fi
    log "Se detuvo $name."
  fi
  rm -f "$pid_file"
}

if [[ "$ACTION" == stop || "$ACTION" == restart ]]; then
  stop_service backend "$BACK_PID_FILE" '-m uvicorn app.main:app'
  stop_service frontend "$FRONT_PID_FILE" "$FRONT_DIR/node_modules/vite/bin/vite.js"
fi

if [[ "$ACTION" == stop ]]; then
  exit 0
fi

if [[ "$ACTION" == status ]]; then
  backend_state=detenido
  frontend_state=detenido
  process_matches "$BACK_PID_FILE" '-m uvicorn app.main:app' && backend_state=activo || true
  process_matches "$FRONT_PID_FILE" "$FRONT_DIR/node_modules/vite/bin/vite.js" && frontend_state=activo || true
  printf 'Backend: %s (http://127.0.0.1:8000/health)\nFrontend: %s (http://127.0.0.1:5173/nuevo-chat)\n' "$backend_state" "$frontend_state"
  exit 0
fi

if process_matches "$BACK_PID_FILE" '-m uvicorn app.main:app' && process_matches "$FRONT_PID_FILE" "$FRONT_DIR/node_modules/vite/bin/vite.js"; then
  log 'El sistema ya está en marcha: http://127.0.0.1:5173/nuevo-chat'
  exit 0
fi

find_python() {
  local candidate version
  for candidate in python3.13 python3.12 python3.11 python3; do
    command -v "$candidate" >/dev/null 2>&1 || continue
    version="$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
    if [[ "$version" =~ ^[0-9]+\.[0-9]+$ ]] && (( ${version%%.*} > 3 || ( ${version%%.*} == 3 && ${version#*.} >= 11 ) )); then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

SYSTEM_PYTHON="$(find_python)" || fail 'Se necesita Python 3.11 o posterior. Instalalo para tu usuario y volvé a ejecutar ./run.sh; no hacen falta permisos sudo.'
NODE_BIN="$(command -v node || true)"
NPM_BIN="$(command -v npm || true)"
[[ -n "$NODE_BIN" && -n "$NPM_BIN" ]] || fail 'Se necesitan Node.js 18 o posterior y npm. Instalalos para tu usuario y volvé a ejecutar ./run.sh; no hacen falta permisos sudo.'
NODE_MAJOR="$("$NODE_BIN" -p 'Number(process.versions.node.split(".")[0])' 2>/dev/null || printf '0')"
[[ "$NODE_MAJOR" =~ ^[0-9]+$ ]] && (( NODE_MAJOR >= 18 )) || fail 'Se necesita Node.js 18 o posterior.'
[[ -f "$FRONT_DIR/package-lock.json" ]] || fail 'Falta front/package-lock.json; no se puede instalar npm de forma reproducible.'

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  log 'Creando el entorno Python local...'
  "$SYSTEM_PYTHON" -m venv "$VENV_DIR" || fail 'No se pudo crear el entorno virtual. Verificá que Python incluya el módulo venv.'
fi
PYTHON="$VENV_DIR/bin/python"

PYPROJECT_HASH="$(sha256sum "$BACK_DIR/pyproject.toml" | cut -d' ' -f1)"
BACKEND_MARKER="$VENV_DIR/.blocia-pyproject-sha256"
if [[ ! -f "$BACKEND_MARKER" || "$(<"$BACKEND_MARKER")" != "$PYPROJECT_HASH" ]] || ! "$PYTHON" -c 'import torch, fastapi, sentence_transformers' >/dev/null 2>&1; then
  log 'Instalando dependencias Python y PyTorch CPU en back/.venv-linux...'
  "$PYTHON" -m pip install --disable-pip-version-check --upgrade pip
  "$PYTHON" -m pip install --disable-pip-version-check --index-url https://download.pytorch.org/whl/cpu 'torch>=2.6'
  (cd "$BACK_DIR" && "$PYTHON" -m pip install --disable-pip-version-check -e '.[local]')
  printf '%s\n' "$PYPROJECT_HASH" > "$BACKEND_MARKER"
fi

PACKAGE_LOCK_HASH="$(sha256sum "$FRONT_DIR/package-lock.json" | cut -d' ' -f1)"
FRONT_MARKER="$FRONT_DIR/node_modules/.blocia-package-lock-sha256"
if [[ ! -x "$FRONT_DIR/node_modules/.bin/vite" || ! -f "$FRONT_MARKER" || "$(<"$FRONT_MARKER" 2>/dev/null || true)" != "$PACKAGE_LOCK_HASH" ]]; then
  log 'Instalando dependencias del frontend con npm ci...'
  (cd "$FRONT_DIR" && "$NPM_BIN" ci --no-audit --no-fund)
  printf '%s\n' "$PACKAGE_LOCK_HASH" > "$FRONT_MARKER"
fi

MODEL_MANIFEST="$BACK_DIR/models/manifest.json"
if [[ ! -f "$MODEL_MANIFEST" ]] || ! "$PYTHON" - "$MODEL_MANIFEST" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1]).parent
try:
    manifest = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    embeddings = manifest.get("embeddings", {})
    chat = manifest.get("chat", {})
    valid = (
        embeddings.get("model") == "intfloat/multilingual-e5-small"
        and embeddings.get("revision") == "614241f622f53c4eeff9890bdc4f31cfecc418b3"
        and chat.get("model") == "Qwen/Qwen3-0.6B"
        and chat.get("revision") == "c1899de289a04d12100db370d81485cdf75e47ca"
    )
    valid &= any((root / "embeddings").glob("*.safetensors")) or any((root / "embeddings").glob("pytorch_model*.bin"))
    valid &= any((root / "chat").glob("*.safetensors")) or any((root / "chat").glob("pytorch_model*.bin"))
    raise SystemExit(0 if valid else 1)
except (OSError, ValueError, TypeError):
    raise SystemExit(1)
PY
then
  log 'Descargando los modelos locales; este paso puede tardar y requiere conexión a internet...'
  (cd "$BACK_DIR" && "$PYTHON" -m ml.prepare)
fi

if ! "$PYTHON" - "$BACK_DIR" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
try:
    classifier = json.loads((root / "ml/artifacts/classifier.json").read_text(encoding="utf-8"))
    report = json.loads((root / "ml/artifacts/training-report.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "models/manifest.json").read_text(encoding="utf-8"))
    encoder = manifest["embeddings"]
    valid = report.get("passed") is True and report.get("encoder") == encoder and classifier.get("encoder") == encoder
    raise SystemExit(0 if valid else 1)
except (OSError, ValueError, KeyError, TypeError):
    raise SystemExit(1)
PY
then
  log 'Actualizando el clasificador para la versión instalada del encoder...'
  (cd "$BACK_DIR" && "$PYTHON" -m ml.train)
fi

port_is_open() {
  (echo > "/dev/tcp/127.0.0.1/$1") >/dev/null 2>&1
}

for port in 8000 5173; do
  if port_is_open "$port"; then
    fail "El puerto $port ya está ocupado. Cerrá el servicio que lo usa o ejecutá ./run.sh stop si lo inició BloqIA."
  fi
done

export FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:5173}"
export BLOCIA_API_URL="${BLOCIA_API_URL:-http://127.0.0.1:8000}"
export GOOGLE_REDIRECT_URI="${GOOGLE_REDIRECT_URI:-http://127.0.0.1:8000/auth/google/callback}"

log 'Iniciando backend y frontend...'
(cd "$BACK_DIR"; nohup "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > "$RUNTIME_DIR/backend.out.log" 2> "$RUNTIME_DIR/backend.err.log" < /dev/null & echo $! > "$BACK_PID_FILE")
(cd "$FRONT_DIR"; nohup "$NODE_BIN" "$FRONT_DIR/node_modules/vite/bin/vite.js" --host 127.0.0.1 --port 5173 --strictPort > "$RUNTIME_DIR/frontend.out.log" 2> "$RUNTIME_DIR/frontend.err.log" < /dev/null & echo $! > "$FRONT_PID_FILE")

wait_for_service() {
  local name="$1" pid_file="$2" expected="$3" port="$4" url="$5" pid
  read -r pid < "$pid_file"
  for _ in {1..120}; do
    if "$PYTHON" -c 'import sys, urllib.request; response = urllib.request.urlopen(sys.argv[1], timeout=1); sys.exit(0 if response.status == 200 else 1)' "$url" >/dev/null 2>&1; then
      return 0
    fi
    if ! process_matches "$pid_file" "$expected"; then
      printf '[BloqIA] Falló el inicio de %s. Últimas líneas del registro:\n' "$name" >&2
      tail -n 40 "$RUNTIME_DIR/${name}.err.log" >&2 || true
      return 1
    fi
    sleep 0.25
  done
  printf '[BloqIA] %s no abrió el puerto %s a tiempo. Revisá back/data/run/%s.err.log.\n' "$name" "$port" "$name" >&2
  return 1
}

if ! wait_for_service backend "$BACK_PID_FILE" '-m uvicorn app.main:app' 8000 'http://127.0.0.1:8000/health'; then
  stop_service backend "$BACK_PID_FILE" '-m uvicorn app.main:app'
  exit 1
fi
if ! wait_for_service frontend "$FRONT_PID_FILE" "$FRONT_DIR/node_modules/vite/bin/vite.js" 5173 'http://127.0.0.1:5173/nuevo-chat'; then
  stop_service frontend "$FRONT_PID_FILE" "$FRONT_DIR/node_modules/vite/bin/vite.js"
  stop_service backend "$BACK_PID_FILE" '-m uvicorn app.main:app'
  exit 1
fi

log 'Sistema listo.'
log 'Abrí http://127.0.0.1:5173/nuevo-chat'
log 'Salud del backend: http://127.0.0.1:8000/health'
log 'Detener: ./run.sh stop | Estado: ./run.sh status'
log "Registros: $RUNTIME_DIR"
