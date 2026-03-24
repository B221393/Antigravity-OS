@echo off
echo ===================================================
echo     EGO DUAL CORE OPERATION SYSTEM
echo ===================================================
echo.
echo [CORE 1] Launching Intelligence Patrol (Deep Loop)...
start "EGO INTELLIGENCE CORE" python c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\shukatsu_patrol.py --auto

echo.
echo [CORE 2] Launching Racing AI (Supercompute Matrix Mode)...
timeout /t 2 >nul
start "EGO RACING AI CORE" cmd /k "cd /d c:\Users\Yuto\Desktop\app\racing_ai_python && 04_TRAIN_HEADLESS_FAST.bat"

echo [CORE 3] Launching System Supervisor AI...
start "EGO SUPERVISOR" python c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\supervisor_ai.py
 
echo [CORE 4] Launching Deep Thinker (Tier 2 Synthesis)...
start "EGO DEEP THINKER" python c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\deep_thinker.py

echo.
echo ===================================================
echo     EGO TRI-CORE SYSTEM ACTIVATED
echo ===================================================
echo.
echo All Cores Activated (Analysis, Racing, Supervisor).
echo Use Alt+Tab to switch between terminals.
echo.
pause
