<#
start_backend.ps1
Starts the FastAPI backend with auto-reload.
Run from the project root: .\start_backend.ps1
#>

$ErrorActionPreference = "Stop"

.\venv\Scripts\Activate.ps1
Push-Location backend
uvicorn app.main:app --reload
Pop-Location
