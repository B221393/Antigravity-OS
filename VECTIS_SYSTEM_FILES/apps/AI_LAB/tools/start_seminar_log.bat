@echo off
cd /d "%~dp0"
echo Starting Seminar Logger...
start /min "SeminarLogger" python seminar_logger.py
echo Logger started in background (minimized).
