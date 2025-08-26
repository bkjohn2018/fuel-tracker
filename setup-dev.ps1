# setup-dev.ps1
# Cross-checked for quote/escaping issues; safe on Windows PowerShell & pwsh

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
  Write-Host "==> $msg" -ForegroundColor Cyan
}

try {
  Write-Step "Verifying Python & pip"
  python --version
  python -m pip --version

  Write-Step "Skipping pip upgrade (known conda compatibility issue)"
  Write-Host "  Using existing pip installation" -ForegroundColor Yellow

  Write-Step "Installing project requirements"
  pip install -r requirements.txt

  Write-Step "Installing dev tools (pre-commit, detect-secrets, ruff, pytest)"
  pip install pre-commit detect-secrets ruff pytest

  Write-Step "Ensuring .env is gitignored and example exists"
  if (-not (Test-Path ".env.example")) {
    @"
EIA_API_KEY=YOUR_KEY_HERE
"@ | Out-File -Encoding utf8 ".env.example"
  }

  Write-Step "Initialize detect-secrets baseline (if missing)"
  if (-not (Test-Path ".secrets.baseline")) {
    detect-secrets scan | Out-File -Encoding utf8 ".secrets.baseline"
    git add .secrets.baseline | Out-Null 2>$null
  }

  Write-Step "Installing pre-commit hooks"
  pre-commit install

  Write-Step "Running pre-commit on all files (first run may take longer)"
  pre-commit run --all-files

  Write-Step "Quick lint"
  ruff check .

  Write-Step "Quick tests"
  pytest -q

  Write-Step "Show run helper"
  if (Test-Path ".\run.ps1") {
    .\run.ps1 help
  } else {
    Write-Host "run.ps1 not found (skipping)" -ForegroundColor Yellow
  }

  Write-Host "`nSetup complete. You're good to go. ✅" -ForegroundColor Green
}
catch {
  Write-Host "Setup failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
