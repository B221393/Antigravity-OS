@echo off
title EGO UNIFIED SYSTEM LAUNCHER
color 0A

echo ================================================
echo   EGO UNIFIED SYSTEM
echo   バケツリレー + Racing AI + ES Generator
echo ================================================
echo.

cd /d "c:\Users\Yuto\Desktop\app"

echo [1/5] Starting PATROL (Collector)...
start "RELAY_PATROL" cmd /k "cd /d c:\Users\Yuto\Desktop\app && .venv\Scripts\activate.bat && python EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\relay_patrol.py"

timeout /t 3 /nobreak > nul

echo [2/5] Starting ANALYZER (AI Analysis)...
start "RELAY_ANALYZER" cmd /k "cd /d c:\Users\Yuto\Desktop\app && .venv\Scripts\activate.bat && python EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\relay_analyzer.py"

timeout /t 3 /nobreak > nul

echo [3/5] Starting REPORTER (Save/Report)...
start "RELAY_REPORTER" cmd /k "cd /d c:\Users\Yuto\Desktop\app && .venv\Scripts\activate.bat && python EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\relay_reporter.py"

timeout /t 3 /nobreak > nul

echo [4/5] Starting RACING AI (Headless Training)...
start "RACING_AI" cmd /k "cd /d c:\Users\Yuto\Desktop\app && .venv\Scripts\activate.bat && python racing_ai_python\train_headless.py"

timeout /t 3 /nobreak > nul

echo [5/5] Starting ES GENERATOR Terminal...
start "ES_GENERATOR" cmd /k "cd /d c:\Users\Yuto\Desktop\app && .venv\Scripts\activate.bat && echo ===== ES Generator Ready ===== && echo Use this terminal for ES creation tasks && cmd"

echo.
echo ================================================
echo   ALL 5 TERMINALS LAUNCHED
echo   
echo   [PATROL]     -> Collects info
echo   [ANALYZER]   -> AI analysis  
echo   [REPORTER]   -> Saves results
echo   [RACING_AI]  -> Car AI training
echo   [ES]         -> Entry Sheet helper
echo.
echo   Close this window or press any key to exit.
echo ================================================
pause
