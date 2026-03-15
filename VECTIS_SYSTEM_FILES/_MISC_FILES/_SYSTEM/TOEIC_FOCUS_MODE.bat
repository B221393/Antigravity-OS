@echo off
setlocal
title [FOCUS] TOEIC Mastery SOLO Mode
cls

echo ==========================================================
echo    TOEIC Mastery Solo Focus Mode
echo ==========================================================
echo.
echo  [CLEANUP] Stopping other VECTIS apps to save memory...
echo.

:: Stop Streamlit and Python background tasks
taskkill /f /im streamlit.exe /t 2>nul
taskkill /f /fi "WINDOWTITLE eq VECTIS_*" /t 2>nul
taskkill /f /im python.exe /t 2>nul

echo  [CLEANUP] Done. System memory reclaimed.
echo.
echo ----------------------------------------------------------
echo  Starting TOEIC Mastery AI... (Port: 5173)
echo ----------------------------------------------------------

cd /d "%~dp0apps\toeic_mastery"

:: Open browser
start http://localhost:5173

:: Run Dev Server
npm run dev

pause
