@echo off
chcp 65001 >nul
title INTELLIGENCE - AUTO PATROL (BOOKSHELF MODE)

echo.
echo ========================================================
echo   INTELLIGENCE: AUTO PATROL (Background System)
echo ========================================================
echo.
echo  [SYSTEM] Initializing Knowledge Acquisition...
echo  [TARGET] UNIVERSE ^& BOOKSHELF
echo  [MODE]   HANDS-FREE (Generating 10k summaries)
echo.

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe apps\MEDIA\INTELLIGENCE_HUB\run_cli.py --auto-universe

pause
