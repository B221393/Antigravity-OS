@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Starting VECTIS HISTORY MODULE...
python -m streamlit run apps\history\app.py
pause
