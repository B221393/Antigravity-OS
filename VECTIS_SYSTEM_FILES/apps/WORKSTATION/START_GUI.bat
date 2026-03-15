@echo off
title VECTIS PRO STATION - GUI Workstation
color 0B

cd /d "c:\Users\Yuto\Desktop\app"

echo Activating Python environment...
call .venv\Scripts\activate.bat

echo [GUI] Launching VECTIS Professional Workstation...
python VECTIS_SYSTEM_FILES\apps\WORKSTATION\VECTIS_PRO_STATION.py

pause
