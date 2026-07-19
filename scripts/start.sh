#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"

if [ ! -x "$ROOT_DIR/backend/.venv/bin/python" ]; then
  echo "Backend environment is missing. Run ./scripts/build.sh first." >&2
  exit 1
fi
if [ ! -f "$ROOT_DIR/frontend/dist/index.html" ]; then
  echo "Frontend build is missing. Run ./scripts/build.sh first." >&2
  exit 1
fi

cd "$ROOT_DIR/backend"
exec .venv/bin/python -m uvicorn app.main:app --host "$HOST" --port "$PORT"
