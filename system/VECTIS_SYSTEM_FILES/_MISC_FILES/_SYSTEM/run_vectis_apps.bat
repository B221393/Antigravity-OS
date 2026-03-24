@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo   VECTIS APPS LAUNCHER (v2.0)
echo ==========================================
echo [1] Launch Secretary (Local Voice/Chat)
echo [2] Launch Job Hunter Dashboard (Knowledge Space)
echo [3] Launch Mobile Bridge Server (FastAPI)
echo [4] Open Output Folder
echo [5] Launch Onishi Typing Trainer
echo [6] Exit
echo ------------------------------------------

set /p choice="Select an app [1-6]: "

if "%choice%"=="1" (
    python orchestrator.py
) else if "%choice%"=="2" (
    python -m streamlit run apps\job_hunting\dashboard.py
) else if "%choice%"=="3" (
    echo Launching Mobile Bridge...
    echo Connect to your PC's IP at port 8000 from mobile.
    start python mobile_bridge.py
    echo Starting Remote Monitor in Orchestrator...
    python orchestrator.py
) else if "%choice%"=="4" (
    start explorer outputs
) else if "%choice%"=="5" (
    python apps\onishi\trainer.py
) else if "%choice%"=="6" (
    exit
) else (
    echo Invalid choice.
    pause
    goto :eof
)
pause
