@echo off
title VECTIS EGO ENGINE
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python run_ego_think.py
pause
