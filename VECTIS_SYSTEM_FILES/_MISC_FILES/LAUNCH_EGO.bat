@echo off
cd /d "%~dp0"
title VECTIS EGO ENGINE
color 0b
echo Launching EGO Evolution Engine...
python apps/ego_evolution/run_ego_cli.py
pause
