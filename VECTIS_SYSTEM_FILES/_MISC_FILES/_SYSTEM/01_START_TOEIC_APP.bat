@echo off
setlocal
title [START] TOEIC PRO (VECTIS ELITE)
cls

echo ==========================================================
echo    START : TOEIC PRO (VECTIS ELITE) - v1.0.0
echo ==========================================================
echo.
echo  1. Advanced Dashboard & Analytics
echo  2. Strategy Hub & Curator Service
echo  3. Interactive Practice Mode
echo.
echo ----------------------------------------------------------
echo  [CLEANUP] Stopping other apps to save memory...
taskkill /f /im streamlit.exe /t 2>nul
echo ----------------------------------------------------------
echo  Starting Development Server...
echo ----------------------------------------------------------

cd /d "%~dp0apps\toeic_pro"

:: Install dependencies if node_modules missing
if not exist "node_modules" (
    echo  [SETUP] Installing dependencies...
    call npm install
)

:: Start Browser
start http://localhost:5173

:: Start Vite Server
call npm run dev

pause
