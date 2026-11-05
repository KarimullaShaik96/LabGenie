@echo off
title LabGenie AI - Intelligent Laboratory Ecosystem
echo ==============================================================
echo LabGenie AI - Intelligent Laboratory Ecosystem
echo Launching Backend and Frontend servers...
echo ==============================================================

start "LabGenie AI - Backend" cmd /c "%~dp0start_backend.bat"
timeout /t 2 /nobreak >nul
start "LabGenie AI - Frontend" cmd /c "%~dp0start_frontend.bat"

echo.
echo Both servers have been launched in separate windows:
echo - Backend: http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo - Frontend: http://localhost:5173
echo.
pause

