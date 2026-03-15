@echo off
chcp 65001 >nul
title ZEN UI - MINIMALIST DASHBOARD

echo.
echo ========================================================
echo   ZEN UI: MINIMALIST DASHBOARD
echo ========================================================
echo.
echo  [SYSTEM] Launching Zen Interface...
echo  [PORT]   8502
echo.

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe -m streamlit run apps\AI_LAB\vectis_omni\app_zen.py --server.port 8502

pause
