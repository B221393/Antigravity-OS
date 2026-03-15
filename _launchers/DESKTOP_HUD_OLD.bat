@echo off
title DESKTOP HUD (LEGACY)

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\pythonw.exe apps\SYSTEM\desktop_hud\hud.py

exit
