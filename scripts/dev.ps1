$root = Split-Path -Parent $PSScriptRoot

$backendPython = "$root\backend\.venv\Scripts\python.exe"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; if (Test-Path '$backendPython') { & '$backendPython' -m uvicorn app.main:app --reload --port 8000 } else { Write-Error 'Missing backend venv: $backendPython' }"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; cmd /c npm run dev"
