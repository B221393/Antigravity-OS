@echo off
title VECTIS AUTO WATCHER
echo.
echo  =======================================================
echo   YouTube URL Watcher Active
echo  =======================================================
echo.
echo   [USAGE]
echo   1. Paste YouTube URL into 'AUTO_YOUTUBE/AUTO_YOUTUBE.txt'
echo   2. Save the file (Ctrl+S)
echo   3. Summary will appear in 'outputs/' folder
echo.
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python scripts/watcher_youtube.py
pause
