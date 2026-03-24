@echo off
cd /d %~dp0
python -m streamlit run apps\diary\app.py
pause
