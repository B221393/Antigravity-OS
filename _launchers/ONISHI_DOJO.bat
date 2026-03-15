@echo off
chcp 65001 >nul
title ONISHI DOJO - TYPING MASTERY

echo.
echo ========================================================
echo   ONISHI DOJO: TYPING MASTERY
echo ========================================================
echo.

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe apps\UTILS\onishi\study_app.py

pause
