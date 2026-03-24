@echo off
title VECTIS Schedule Watcher - 自動壁紙更新
color 0B

cd /d "c:\Users\Yuto\Desktop\app"

echo ====================================
echo  VECTIS Schedule Wallpaper Watcher
echo ====================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo 必要なパッケージを確認中...
pip install watchdog -q

echo.
python VECTIS_SYSTEM_FILES\bin\schedule_wallpaper_watcher.py

pause
