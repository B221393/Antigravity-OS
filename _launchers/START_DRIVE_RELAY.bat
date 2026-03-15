@echo off
title Google Drive Relay Server
set APP_DIR=C:\Users\Yuto\desktop\app
cd /d %APP_DIR%

echo [INFO] Working directory: %APP_DIR%

:: Virtual environment check
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
)

echo [INFO] Checking dependencies...
.venv\Scripts\python.exe -m pip install --quiet google-api-python-client google-auth-httplib2 google-auth-oauthlib

:: Run script
echo [INFO] Starting relay server...
.venv\Scripts\python.exe python_scripts\drive_relay.py

pause
