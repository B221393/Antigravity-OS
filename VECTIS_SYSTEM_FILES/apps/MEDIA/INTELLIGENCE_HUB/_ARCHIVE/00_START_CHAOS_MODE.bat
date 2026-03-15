@echo off
setlocal
cd /d "%~dp0"

echo.
echo ===========================================
echo   🌀 VECTIS INTELLIGENCE: CHAOS MODE
echo ===========================================
echo   Starting patrol with expanded/random sources.
echo   Goal: Break filter bubbles & Discover new ideas.
echo.

python run_cli.py --chaos

echo.
echo   Press any key to exit...
pause >nul
