[CmdletBinding()]
param(
  [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$python = Join-Path $backend ".venv\Scripts\python.exe"
$index = Join-Path $root "frontend\dist\index.html"

if (-not (Test-Path -LiteralPath $python) -or -not (Test-Path -LiteralPath $index)) {
  throw "Build artifacts are missing. Run .\scripts\build.ps1 first."
}

$process = Start-Process `
  -FilePath $python `
  -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $Port) `
  -WorkingDirectory $backend `
  -WindowStyle Hidden `
  -PassThru

try {
  $ready = $false
  for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
      $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
      if ($health.status -eq "ok") {
        $ready = $true
        break
      }
    }
    catch {
      Start-Sleep -Milliseconds 250
    }
  }

  if (-not $ready) {
    throw "Server did not become healthy."
  }

  $homeResponse = Invoke-WebRequest `
    -Uri "http://127.0.0.1:$Port/" `
    -UseBasicParsing `
    -TimeoutSec 5
  if (
    $homeResponse.StatusCode -ne 200 -or
    $homeResponse.Content -notmatch '<div id="root"></div>'
  ) {
    throw "Frontend response validation failed."
  }

  Write-Host "Smoke test passed: API health and frontend index are available."
}
finally {
  if (-not $process.HasExited) {
    Stop-Process -Id $process.Id
    $process.WaitForExit()
  }
}
