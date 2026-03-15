@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo   EGO HEALTH MONITOR (CAMEL-AI)
echo   Every 30 Minutes Sync
echo ============================================
echo.

:loop
echo [%time%] Running System Health Audit...
..\..\..\..\.venv\Scripts\python.exe check_system_health.py

echo.
echo [%time%] Audit complete. Next check in 30 minutes.
echo Close this window to stop monitoring.
timeout /t 1800 /nobreak >nul
goto loop
