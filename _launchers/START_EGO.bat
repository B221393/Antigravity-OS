@echo off
setlocal
cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"

REM Reset log file
echo [INFO] BOOT SEQUENCE STARTED > logs\ego_boot_log.txt
echo [INFO] Timestamp: %DATE% %TIME% >> logs\ego_boot_log.txt
echo [INFO] Current Directory: %CD% >> logs\ego_boot_log.txt

REM 1. Search for Python
set "VENV_PYTHON=..\.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo [INFO] Found Venv: %VENV_PYTHON% >> logs\ego_boot_log.txt
    set "TARGET_PYTHON=%VENV_PYTHON%"
) else (
    echo [WARNING] Venv not found. Fallback to system 'python'. >> logs\ego_boot_log.txt
    set "TARGET_PYTHON=python"
)

echo [INFO] Target Python: %TARGET_PYTHON% >> logs\ego_boot_log.txt

REM 2. Launch GUI
echo [INFO] Launching Native Independent Mode... >> logs\ego_boot_log.txt

"%TARGET_PYTHON%" EGO_OMNI_EXPLORER.py >> logs\ego_boot_log.txt 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL ERROR] Failed to launch.
    echo Please check 'VECTIS_SYSTEM_FILES\logs\ego_boot_log.txt' for details.
    echo.
    echo === LOG PREVIEW ===
    type logs\ego_boot_log.txt
    echo ===================
    pause
) else (
    echo [INFO] Application exited normally. >> logs\ego_boot_log.txt
)
