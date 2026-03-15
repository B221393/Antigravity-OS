@echo off
chcp 65001 >nul
title OMNI - COMMAND CENTER

echo.
echo ========================================================
echo   OMNI: COMMAND CENTER
echo ========================================================
echo.
echo  [SYSTEM] Launching Dashboard...
echo  [PORT]   8501
echo.

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe -m streamlit run apps\AI_LAB\vectis_omni\app_glass.py --server.port 8501

pause
