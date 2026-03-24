@echo off
setlocal
set LOGFILE=c:\Users\Yuto\Desktop\app\VECTIS_LOGS\04_ES_WRITER_%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%.log
set LOGFILE=%LOGFILE: =0%
echo [START] Launching ES WRITER at %date% %time% >> "%LOGFILE%"

cd /d "%~dp0..\.."
call .venv\Scripts\activate

echo [INFO] Starting ES Assistant... >> "%LOGFILE%"
streamlit run VECTIS_SYSTEM_FILES/apps/es_assistant/app.py >> "%LOGFILE%" 2>&1

echo [END] Session End >> "%LOGFILE%"
endlocal
pause
