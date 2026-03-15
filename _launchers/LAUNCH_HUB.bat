@echo off
title HUB - Command Center
color 0B

cd /d "%~dp0\.."

echo Activating Environment...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [WARN] .venv not found.
)

echo.
echo [SYSTEM] Launching Hub...
python VECTIS_SYSTEM_FILES\vectis_hub.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Launcher crashed with code %errorlevel%.
    pause
)
