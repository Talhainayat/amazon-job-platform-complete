@echo off
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Purani chalti hui instances ko terminate karein
taskkill /FI "WINDOWTITLE eq Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend*" /F >nul 2>&1

:: Background process start karein
start "Backend" /min cmd /c "powershell -ExecutionPolicy Bypass -File .\start_backend.ps1"
start "Frontend" /min cmd /c "powershell -ExecutionPolicy Bypass -File .\start_frontend.ps1"

:: Browser instant open karein
timeout /t 2 /nobreak >nul
start http://localhost:5173

exit