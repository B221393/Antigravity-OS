@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
    echo Drag and drop a zip file onto this script to extract it.
    pause
    exit /b
)

set "ZIP_FILE=%~1"
set "OUT_DIR=%~dpn1"

echo Extracting "%ZIP_FILE%" to "%OUT_DIR%"...

powershell -command "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%OUT_DIR%' -Force"

if %errorlevel% neq 0 (
    echo Extraction failed.
    pause
) else (
    echo Extraction complete.
    start "" "%OUT_DIR%"
)
