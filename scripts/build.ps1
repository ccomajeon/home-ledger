[CmdletBinding()]
param(
  [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$venvPython = Join-Path $backend ".venv\Scripts\python.exe"

function Assert-NativeSuccess {
  param([string]$Step)

  if ($LASTEXITCODE -ne 0) {
    throw "$Step failed with exit code $LASTEXITCODE."
  }
}

function New-BackendEnvironment {
  if (Test-Path -LiteralPath $venvPython) {
    return
  }

  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    & $python.Source -m venv (Join-Path $backend ".venv")
    Assert-NativeSuccess "Creating the backend environment"
    return
  }

  $launcher = Get-Command py -ErrorAction SilentlyContinue
  if ($launcher) {
    & $launcher.Source -3 -m venv (Join-Path $backend ".venv")
    Assert-NativeSuccess "Creating the backend environment"
    return
  }

  throw "Python 3.11 or later is required."
}

Write-Host "[1/4] Preparing backend environment"
New-BackendEnvironment
Push-Location $backend
try {
  & $venvPython -m pip install -e ".[dev]"
  Assert-NativeSuccess "Installing backend dependencies"
  if (-not $SkipTests) {
    & $venvPython -m black --check app tests
    Assert-NativeSuccess "Checking backend formatting"
    & $venvPython -m ruff check app tests
    Assert-NativeSuccess "Linting the backend"
    & $venvPython -m pytest -q --basetemp=.pytest-build
    Assert-NativeSuccess "Testing the backend"
  }
  & $venvPython -c "from app.db.base import Base; from app.db.session import SessionLocal, engine; from app.db.seed import seed_defaults; Base.metadata.create_all(bind=engine); db = SessionLocal(); seed_defaults(db); db.close()"
  Assert-NativeSuccess "Preparing the database"
}
finally {
  Pop-Location
}

Write-Host "[2/4] Installing frontend dependencies"
$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) {
  throw "Node.js 20 or later with npm is required."
}
Push-Location $frontend
try {
  & $npm.Source ci
  Assert-NativeSuccess "Installing frontend dependencies"
  if (-not $SkipTests) {
    Write-Host "[3/4] Testing frontend"
    & $npm.Source run format
    Assert-NativeSuccess "Checking frontend formatting"
    & $npm.Source run lint
    Assert-NativeSuccess "Linting the frontend"
    & $npm.Source run test
    Assert-NativeSuccess "Testing the frontend"
  }
  Write-Host "[4/4] Building frontend"
  & $npm.Source run build
  Assert-NativeSuccess "Building the frontend"
}
finally {
  Pop-Location
}

Write-Host "Build completed. Run .\scripts\start.ps1 to start Home Ledger."
