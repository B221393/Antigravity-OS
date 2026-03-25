@echo off
title QUMI INTEGRATED OS - CORE LAUNCHER
echo ========================================================
echo   QUMI INTEGRATED OS - CORE SYSTEM BOOT
echo ========================================================
echo.

:: Check for .env in backend
if not exist "Qumi_Core\backend\.env" (
    echo [WARN] Qumi_Core\backend\.env not found. 
    echo [WARN] Please ensure GEMINI_API_KEY is set.
)

:: Start MetaClaw Proxy (Background)
echo [1/2] Starting MetaClaw Intelligence Proxy...
start /b cmd /c ".venv\Scripts\metaclaw.exe start --mode skills_only"

:: Wait for MetaClaw to warm up
timeout /t 5 > nul

:: Start Qumi Backend Hub
echo [2/2] Starting Qumi Backend Hub (FastAPI)...
cd Qumi_Core\backend
..\..\.venv\Scripts\python.exe main.py

pause
