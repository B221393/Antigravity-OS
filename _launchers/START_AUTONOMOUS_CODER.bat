@echo off
echo ==================================================
echo   AUTONOMOUS CODER - BOOT SEQUENCE INITIATED
echo ==================================================
cd /d "%~dp0\.."
python python_scripts\autonomous_coder.py
echo ==================================================
echo   PROCESS COMPLETED. THIS WINDOW WILL CLOSE IN 5s
echo ==================================================
timeout /t 5 >nul
exit
