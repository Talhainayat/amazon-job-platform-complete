<#
setup.ps1
One-time local setup for amazon-job-platform.
Run this from the project root:  .\setup.ps1

What it does:
  1. Creates/reuses the Python venv
  2. Installs backend dependencies from backend\requirements.txt
  3. Copies .env.example to .env if .env doesn't exist yet
  4. Runs Alembic migrations against the configured DATABASE_URL
  5. Installs frontend dependencies (npm install)

What it does NOT do:
  - Does not install PostgreSQL or Redis themselves (see README.md)
  - Does not overwrite an existing .env file
#>

$ErrorActionPreference = "Stop"

Write-Host "== 1. Python virtual environment ==" -ForegroundColor Cyan
if (-not (Test-Path ".\venv")) {
    python -m venv venv
    Write-Host "Created venv."
} else {
    Write-Host "venv already exists, reusing it."
}

Write-Host "== 2. Activating venv and installing backend dependencies ==" -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

Write-Host "== 3. Environment file ==" -ForegroundColor Cyan
if (-not (Test-Path ".\.env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Edit it with your real local values (DATABASE_URL, SECRET_KEY, etc)."
} else {
    Write-Host ".env already exists, leaving it untouched."
}

Write-Host "== 4. Database migrations ==" -ForegroundColor Cyan
Write-Host "This will run 'alembic upgrade head' using the DATABASE_URL in your .env file."
Write-Host "Default is SQLite (zero setup). If you've switched to Postgres, make sure the server is running first."
Push-Location backend
alembic upgrade head
Pop-Location

Write-Host "== 5. Frontend dependencies ==" -ForegroundColor Cyan
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Push-Location frontend
    npm install
    Pop-Location
} else {
    Write-Host "npm not found - skipping frontend install. Install Node.js, then run 'npm install' inside frontend\ manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Next: .\start_backend.ps1  (in one terminal)"
Write-Host "      .\start_frontend.ps1 (in another terminal)"
