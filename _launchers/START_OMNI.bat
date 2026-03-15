@echo off
setlocal
cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"

REM Reset log file
echo [INFO] OMNI BOOT SEQUENCE STARTED > logs\omni_boot_log.txt
echo [INFO] Timestamp: %DATE% %TIME% >> logs\omni_boot_log.txt

REM 1. Search for Python
set "VENV_PYTHON=..\.venv\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    echo [INFO] Found Venv: %VENV_PYTHON% >> logs\omni_boot_log.txt
    set "TARGET_PYTHON=%VENV_PYTHON%"
) else (
    echo [WARNING] Venv not found. Fallback to system 'python'. >> logs\omni_boot_log.txt
    set "TARGET_PYTHON=python"
)

echo [INFO] Target Python: %TARGET_PYTHON% >> logs\omni_boot_log.txt

REM 2. Launch OMNI EXPLORER
echo [INFO] Launching OMNI EXPLORER... >> logs\omni_boot_log.txt

"%TARGET_PYTHON%" EGO_OMNI_EXPLORER.py >> logs\omni_boot_log.txt 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL ERROR] Failed to launch OMNI.
    echo Please check 'VECTIS_SYSTEM_FILES\logs\omni_boot_log.txt' for details.
    echo.
    type logs\omni_boot_log.txt
    pause
) else (
    echo [INFO] Application exited normally. >> logs\omni_boot_log.txt
)
endlocal
