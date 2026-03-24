@echo off
setlocal
title START ONISHI LAYOUT

echo ==========================================================
echo    START : ONISHI o24 LAYOUT
echo ==========================================================
echo.
echo  [SYSTEM] Preparing environment...

:: Ensure any existing instances are closed first to prevent duplicates
powershell -NoProfile -Command "Get-Process | Where-Object { $_.ProcessName -like '*AutoHotkey*' } | Stop-Process -Force -ErrorAction SilentlyContinue"

echo  [SYSTEM] Launching AutoHotkey script...

:: Launch the script
start "" "%~dp0onishi_layout.ahk"

if %errorlevel% equ 0 (
    echo.
    echo  [SUCCESS] Onishi Layout Activated.
    echo  To Restore Qwerty:
    echo    1. Press 'Qwerty' button in the App
    echo    2. Or run 02_Restore_Qwerty.bat
) else (
    echo.
    echo  [ERROR] Failed to launch onishi_layout.ahk.
    echo  Please ensure AutoHotkey v1.1+ is installed and associated with .ahk files.
)

echo.
echo Closing in 2 seconds...
timeout /t 2 >nul
exit
