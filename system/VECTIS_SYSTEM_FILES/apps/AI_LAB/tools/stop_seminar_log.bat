@echo off
cd /d "%~dp0"
set PID_FILE=seminar_logger.pid

if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    echo Stopping Seminar Logger (PID: %PID%)...
    taskkill /PID %PID% /F
    del "%PID_FILE%"
    echo Stopped.
) else (
    echo Seminar Logger is not running (PID file not found).
)
pause
