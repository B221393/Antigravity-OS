@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run apps\youtube_channel\app.py --server.port 8519
pause
