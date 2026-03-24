@echo off
setlocal
set LOGFILE=c:\Users\Yuto\Desktop\app\VECTIS_LOGS\03_JOB_PATROL_%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%.log
set LOGFILE=%LOGFILE: =0%
echo [START] Launching JOB PATROL at %date% %time% >> "%LOGFILE%"

cd /d "%~dp0"
call .venv\Scripts\activate

echo [INFO] Starting Intelligence Patrol (Automated)... >> "%LOGFILE%"
call "202_INFO_PATROL.bat" >> "%LOGFILE%" 2>&1

echo [END] Session End >> "%LOGFILE%"
endlocal
pause
