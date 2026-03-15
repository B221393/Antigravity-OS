@echo off
setlocal
set LOGFILE=c:\Users\Yuto\Desktop\app\VECTIS_LOGS\05_MY_EGO_%date:~0,4%-%date:~5,2%-%date:~8,2%_%time:~0,2%-%time:~3,2%.log
set LOGFILE=%LOGFILE: =0%
echo [START] Launching EGO CORE at %date% %time% >> "%LOGFILE%"

cd /d "%~dp0"
call .venv\Scripts\activate

echo [INFO] Starting Ego Core / Personal Agent... >> "%LOGFILE%"
:: Prefer Launching Personal Agent Wrapper if it exists, otherwise Ego Core
if exist "200_INFO_PERSONAL_AGENT.bat" (
    call "200_INFO_PERSONAL_AGENT.bat" >> "%LOGFILE%" 2>&1
) else (
    call "102_AI_EGO_CORE.bat" >> "%LOGFILE%" 2>&1
)

echo [END] Session End >> "%LOGFILE%"
endlocal
pause
