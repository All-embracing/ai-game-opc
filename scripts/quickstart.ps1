# Run inside the opc-game-studio folder: powershell -ExecutionPolicy Bypass -File scripts/quickstart.ps1
# Does not create accounts, change billings, request credentials or push to GitHub.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
Write-Host "[OPC] Running local tests..."
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Python test suite failed" }
Write-Host "[OPC] Running deployment preflight (no credential access)..."
python scripts/doctor.py
if ($LASTEXITCODE -ne 0) { throw "Preflight failed" }
Write-Host "[OPC] Open the browser game locally at games/emotion-garden/index.html"
Write-Host "[OPC] Next: follow docs/05-OPC-execution-playbook.md"
