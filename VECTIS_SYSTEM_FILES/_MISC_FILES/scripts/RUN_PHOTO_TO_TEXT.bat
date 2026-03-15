@echo off
setlocal
title VECTIS // PHOTO TO TEXT (GEMINI OCR)

:: Check if file was dropped
if "%~1"=="" (
    echo ========================================================
    echo   VECTIS OCR TOOL
    echo   Usage: Drag and drop an image file onto this .bat
    echo ========================================================
    pause
    exit /b
)

:: Run Python Script
cd /d "%~dp0"
python photo_to_text.py "%~1"

pause
