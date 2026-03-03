#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR/backend"
if [ ! -x ".venv/bin/python" ]; then
  echo "backend virtual environment not found: .venv/bin/python" >&2
  exit 1
fi

.venv/bin/python -c "from app.db.base import Base; from app.db.session import SessionLocal, engine; from app.db.seed import seed_defaults; Base.metadata.create_all(bind=engine); db = SessionLocal(); seed_defaults(db); db.close()"
