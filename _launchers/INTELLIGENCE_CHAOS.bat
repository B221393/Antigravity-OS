@echo off
chcp 65001 >nul
title INTELLIGENCE - CHAOS PATROL (CURIOSITY MODE)

echo.
echo ========================================================
echo   INTELLIGENCE: CHAOS PATROL (Curiosity Engine)
echo ========================================================
echo.
echo  [SYSTEM] Initializing Curiosity Injection...
echo  [TARGET] KARAPAIA / NAZOLOGY / NATGEO
echo  [MODE]   CHAOS (Business/Tech Expunged)
echo.

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe apps\MEDIA\INTELLIGENCE_HUB\run_cli.py --auto-universe --chaos

pause
