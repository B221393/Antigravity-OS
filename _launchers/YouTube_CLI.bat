@echo off
color 0B
title TERMINAL [CHANNEL DIGEST]

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe apps\MEDIA\INTELLIGENCE_HUB\run_cli.py

pause
