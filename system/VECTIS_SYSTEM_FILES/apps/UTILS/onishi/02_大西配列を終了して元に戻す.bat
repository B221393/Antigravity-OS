@echo off
setlocal
title RESTORE QWERTY LAYOUT

echo ==========================================================
echo    RESTORE : ORIGINAL QWERTY (Windows Default)
echo ==========================================================
echo.
echo  [SYSTEM] Stopping all AutoHotkey processes...

:: PowerShell to kill any process matching "AutoHotkey" (case-insensitive)
powershell -NoProfile -Command "Get-Process | Where-Object { $_.ProcessName -like '*AutoHotkey*' } | Stop-Process -Force -ErrorAction SilentlyContinue"

if %errorlevel% equ 0 (
    echo.
    echo  [SUCCESS] All AutoHotkey scripts have been terminated.
    echo  Keyboard is now back to QWERTY.
) else (
    echo.
    echo  [INFO] No active AutoHotkey processes found.
)

echo.
echo Closing in 2 seconds...
timeout /t 2 >nul
exit
