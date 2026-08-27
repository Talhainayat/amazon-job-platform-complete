<#
start_frontend.ps1
Starts the Vite dev server for the React frontend.
Run from the project root: .\start_frontend.ps1
#>

$ErrorActionPreference = "Stop"

Push-Location frontend
npm run dev
Pop-Location
