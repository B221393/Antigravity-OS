@echo off
cd /d %~dp0
python -m streamlit run apps\job_hunting\dashboard.py
pause
