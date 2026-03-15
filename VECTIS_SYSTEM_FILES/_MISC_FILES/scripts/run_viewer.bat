@echo off
echo [INFO] Legacy Viewer is deprecated. Launching Job Hunter Dashboard...
cd /d %~dp0
python -m streamlit run apps\job_hunting\dashboard.py
pause
