@echo off
title [AUTO] YouTube Watcher
echo.
echo  =======================================================
echo   YouTube URL Watcher Active
echo  =======================================================
echo.
echo   [USAGE]
echo   1. Paste YouTube URL into 'AUTO_YOUTUBE.txt'
echo   2. Save the file (Ctrl+S)
echo   3. Summary will appear in '../outputs/' folder
echo.
echo   Watching... (Press Ctrl+C to stop)
echo.

cd /d "%~dp0"
..\..\.venv\Scripts\python.exe ../scripts/watcher_youtube.py

:: 収集完了後に重複削除を自動実行
echo.
echo 🧹 重複削除を実行中...
call AUTO_DEDUPE.bat

pause
