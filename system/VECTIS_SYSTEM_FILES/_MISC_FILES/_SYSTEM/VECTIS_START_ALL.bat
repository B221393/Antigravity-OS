@echo off
setlocal
title VECTIS OS - AUTO BOOT

:: Simple English messages to avoid any encoding quirks during boot
echo ==========================================
echo    VECTIS OS : BOOTING SYSTEMS
echo ==========================================
echo.

:: Ensure streamlit is installed
echo [DEBUG] Checking environment...
python -m streamlit --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [SYSTEM] Streamlit not found. Installing now...
    python -m pip install streamlit
)

echo [1/5] Launching HUB: Job Hunter (8501)
start "VECTIS_8501" /min cmd /c "cd /d %~dp0apps\job_hunting && python -m streamlit run dashboard.py --server.port 8501 --server.headless true"

echo [2/5] Launching HUB: TOEIC Mastery (8502)
start "VECTIS_8502" /min cmd /c "cd /d %~dp0apps\toeic && python -m streamlit run app.py --server.port 8502 --server.headless true"

echo [3/5] Launching HUB: Life Diary (8503)
start "VECTIS_8503" /min cmd /c "cd /d %~dp0apps\diary && python -m streamlit run app.py --server.port 8503 --server.headless true"

echo [4/5] Launching HUB: System Monitor (8504)
start "VECTIS_8504" /min cmd /c "cd /d %~dp0apps\system_monitor && python -m streamlit run app.py --server.port 8504 --server.headless true"

echo [5/11] Launching HUB: History (8505)
start "VECTIS_8505" /min cmd /c "cd /d %~dp0apps\history && python -m streamlit run app.py --server.port 8505 --server.headless true"

echo [6/11] Launching HUB: ES Master (8506)
start "VECTIS_8506" /min cmd /c "cd /d %~dp0apps\es_assistant && python -m streamlit run app.py --server.port 8506 --server.headless true"

echo [7/11] Launching HUB: Creator (8507)
start "VECTIS_8507" /min cmd /c "cd /d %~dp0apps\creator && python -m streamlit run app.py --server.port 8507 --server.headless true"

echo [8/11] Launching HUB: Helper (8508)
start "VECTIS_8508" /min cmd /c "cd /d %~dp0apps\help && python -m streamlit run app.py --server.port 8508 --server.headless true"

echo [9/11] Launching HUB: Scout (8509)
start "VECTIS_8509" /min cmd /c "cd /d %~dp0apps\scout && python -m streamlit run app.py --server.port 8509 --server.headless true"

echo [10/11] Launching HUB: Stats (8510)
start "VECTIS_8510" /min cmd /c "cd /d %~dp0apps\stats && python -m streamlit run app.py --server.port 8510 --server.headless true"

echo [11/13] Launching HUB: Stream (8511)
start "VECTIS_8511" /min cmd /c "cd /d %~dp0apps\stream && python -m streamlit run app.py --server.port 8511 --server.headless true"

echo [12/13] Launching HUB: Memory (8512)
start "VECTIS_8512" /min cmd /c "cd /d %~dp0apps\memory && python -m streamlit run app.py --server.port 8512 --server.headless true"

echo [13/14] Launching HUB: Link (8513)
start "VECTIS_8513" /min cmd /c "cd /d %~dp0apps\link && python -m streamlit run app.py --server.port 8513 --server.headless true"

echo [14/16] Launching HUB: Mobile (8514)
start "VECTIS_8514" /min cmd /c "cd /d %~dp0apps\mobile && python -m streamlit run app.py --server.port 8514 --server.headless true"

echo [15/16] Launching HUB: Calendar (8515)
start "VECTIS_8515" /min cmd /c "cd /d %~dp0apps\calendar && python -m streamlit run app.py --server.port 8515 --server.headless true"

echo [16/17] Launching HUB: Trivia (8516)
start "VECTIS_8516" /min cmd /c "cd /d %~dp0apps\trivia && python -m streamlit run app.py --server.port 8516 --server.headless true"

echo [17/17] Launching HUB: Job HQ (8517)
start "VECTIS_8517" /min cmd /c "cd /d %~dp0apps\job_hq && python -m streamlit run app.py --server.port 8517 --server.headless true"

echo.
echo Systems are initializing.
echo Hub will open in 5 seconds...
timeout /t 5 /nobreak >nul

start "" "%~dp0apps\dashboard\index.html"

echo.
echo ==========================================
echo    VECTIS IS ONLINE. STAY FOCUSED.
echo    * To close all windows, run VECTIS_STOP_ALL.bat
echo ==========================================
echo Done.
pause
