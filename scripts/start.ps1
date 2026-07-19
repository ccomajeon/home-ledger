[CmdletBinding()]
param(
  [int]$Port = 8000,
  [string]$HostAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontendDist = Join-Path $root "frontend\dist"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
  throw "Backend environment is missing. Run .\scripts\build.ps1 first."
}
if (-not (Test-Path -LiteralPath (Join-Path $frontendDist "index.html"))) {
  throw "Frontend build is missing. Run .\scripts\build.ps1 first."
}

Write-Host "Home Ledger is starting at http://${HostAddress}:$Port"
Push-Location $backend
try {
  & $python -m uvicorn app.main:app --host $HostAddress --port $Port
}
finally {
  Pop-Location
}
