@echo off
title EGO VISUAL ARCHIVE
echo ========================================================
echo   EGO VISUAL ARCHIVE (3D Bookshelf)
echo ========================================================
echo.
echo  [SYSTEM] Launching Flask Backend...
echo  [PORT]   5050
echo.

cd /d "%~dp0"
:: Assuming EGO_SYSTEM_FILES structure, go up to app root to activate venv if needed
:: But typically python in path or .venv is at root of app workspace
:: Adjusted for provided path c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES\apps\MEDIA\bookshelf_gallery
cd ..\..\..\..\

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate
)

cd EGO_SYSTEM_FILES\apps\MEDIA\bookshelf_gallery
start http://localhost:5050
python app.py

pause
