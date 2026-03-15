@echo off
title CHANNEL DIGEST (WEB)

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe -m streamlit run apps\MEDIA\INTELLIGENCE_HUB\EGO_SHUKATSU_HQ_APP.py --server.port 8519

pause
