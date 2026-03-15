@echo off
title VIBE CODING OVERLAY HUD
cd /d "%~dp0"
echo ========================================================
echo   VIBE CODING OVERLAY HUD
echo ========================================================
echo.
echo  [SYSTEM] Stopping existing overlay instances...
wmic process where "CommandLine like '%%overlay.py%%'" call terminate >nul 2>&1

echo  [SYSTEM] Installing dependencies (PyQt6, keyboard)...

if exist "..\..\..\..\.venv\Scripts\activate.bat" (
    call "..\..\..\..\.venv\Scripts\activate.bat"
) else (
    echo [WARNING] No venv found. Installing to global python or creaing new venv recommended.
    echo Trying global python...
)

pip install PyQt6 keyboard

echo.
echo  [SYSTEM] Launching Overlay...
echo  (Press Ctrl+C in this terminal to close, or close via Task Manager)
echo.

python overlay.py
pause
