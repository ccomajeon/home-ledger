#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [ ! -x "$BACKEND_DIR/.venv/bin/python" ]; then
  python3 -m venv "$BACKEND_DIR/.venv"
fi

(
  cd "$BACKEND_DIR"
  .venv/bin/python -m pip install -e ".[dev]"
  .venv/bin/python -m black --check app tests
  .venv/bin/python -m ruff check app tests
  .venv/bin/python -m pytest -q --basetemp=.pytest-build
  .venv/bin/python -c "from app.db.base import Base; from app.db.session import SessionLocal, engine; from app.db.seed import seed_defaults; Base.metadata.create_all(bind=engine); db = SessionLocal(); seed_defaults(db); db.close()"
)

(
  cd "$FRONTEND_DIR"
  npm ci
  npm run format
  npm run lint
  npm run test
  npm run build
)

echo "Build completed. Run ./scripts/start.sh to start Home Ledger."
