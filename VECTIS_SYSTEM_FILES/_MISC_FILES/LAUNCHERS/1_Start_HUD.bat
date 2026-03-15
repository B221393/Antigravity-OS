@echo off
title VECTIS HUD
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
streamlit run apps\desktop_hud\app.py --server.port 8515
pause
