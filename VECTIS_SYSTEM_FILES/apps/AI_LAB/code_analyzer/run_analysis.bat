@echo off
title VECTIS CODE ANALYZER
echo ========================================================
echo   VECTIS CODE ANALYZER (Python AST + Mermaid)
echo ========================================================
echo.
echo  Usage: Drag and drop a folder onto this script,
echo         or type the path below.
echo.

cd /d "%~dp0"

:: Activate venv if exists
if exist "..\..\..\..\.venv\Scripts\activate.bat" (
    call "..\..\..\..\.venv\Scripts\activate.bat"
)

set TARGET_DIR=%1
if "%TARGET_DIR%"=="" set /p TARGET_DIR="Target Directory Path > "

if "%TARGET_DIR%"=="" (
    echo No directory specified. Exiting.
    pause
    exit /b
)

echo.
echo Analyzing: %TARGET_DIR%
echo output will be saved to: %TARGET_DIR%\_analysis_output
echo.

python analyzer.py "%TARGET_DIR%"

echo.
echo Analysis Complete.
echo Check the _analysis_output folder in the target directory.
echo.
pause
