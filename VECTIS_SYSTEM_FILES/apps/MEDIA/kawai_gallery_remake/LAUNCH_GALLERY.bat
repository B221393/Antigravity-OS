@echo off
title KAWAI GALLERY REMAKE (Standalone)
echo ========================================================
echo   KAWAI GALLERY REMAKE (Flask App)
echo ========================================================
echo.
echo  [SYSTEM] Launching Flask Backend...
echo  [PORT]   5052
echo.

cd /d "%~dp0"
:: Assuming standardized venv structure at app root or one level up
:: Going up to app root from apps/MEDIA/kawai_gallery_remake (4 levels up from inside script?)
:: Actually, let's just use python from path or check standard venv location

if exist "..\..\..\..\.venv\Scripts\activate.bat" (
    call "..\..\..\..\.venv\Scripts\activate.bat"
)

start http://localhost:5052
python app.py
pause
