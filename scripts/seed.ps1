$root = Split-Path -Parent $PSScriptRoot

Set-Location "$root\backend"
$pythonPath = ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
  throw "backend virtual environment not found: $pythonPath"
}

& $pythonPath -c "from app.db.base import Base; from app.db.session import SessionLocal, engine; from app.db.seed import seed_defaults; Base.metadata.create_all(bind=engine); db = SessionLocal(); seed_defaults(db); db.close()"
