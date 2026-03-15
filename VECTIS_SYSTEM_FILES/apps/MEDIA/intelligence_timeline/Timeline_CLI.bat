@echo off
title VECTIS INTELLIGENCE VIEWER
color 0b
echo ==================================================
echo   VECTIS CLI INTELLIGENCE SYSTEM
echo   Initializing...
echo ==================================================
echo.

cd /d "%~dp0"
python timeline_cli.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] System crashed or exited with error.
    pause
)
