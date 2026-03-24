@echo off
setlocal
title VECTIS OS - CLEANUP

echo ==========================================
echo    VECTIS OS : SYSTEM SHUTDOWN
echo ==========================================
echo.

echo [INFO]echo Stopping all 14 Streamlit Servers (Ports 8501-8514)...
taskkill /f /im streamlit.exe /t 2>nul

echo [INFO] Cleaning up background Python tasks...
taskkill /f /fi "WINDOWTITLE eq VECTIS_*" /t 2>nul

echo.
echo ==========================================
echo    ROADS CLEARED. 
echo ==========================================
echo Done.
timeout /t 3
exit
