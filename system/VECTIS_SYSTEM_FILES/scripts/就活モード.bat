@echo off
chcp 65001 > nul
title 👔 就活バトルモード 👔

echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║          👔 就活バトルモード 起動 👔                ║
echo ║                                                   ║
echo ║   1. 📡 情報パトロール (Shukatsu Patrol)          ║
echo ║   2. 🌌 アプリブラウザ (Base Camp)                ║
echo ╚═══════════════════════════════════════════════════╝
echo.

echo 📡 Step 1: 最新情報を確保します...
cd /d "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES"
start "Shukatsu Patrol" cmd /c "python apps/MEDIA/INTELLIGENCE_HUB/shukatsu_patrol.py & pause"

echo 🌌 Step 2: ベースキャンプ（アプリブラウザ）を開きます...
python bin/apps_browser.py

echo.
echo ✅ バトルモード終了
pause
