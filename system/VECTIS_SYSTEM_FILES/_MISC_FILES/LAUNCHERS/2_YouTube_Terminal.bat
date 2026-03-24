@echo off
color 0B
title VECTIS TERMINAL [CHANNEL DIGEST]
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python apps\youtube_channel\run_cli.py
pause
