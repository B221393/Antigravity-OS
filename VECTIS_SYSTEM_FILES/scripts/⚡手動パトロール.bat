@echo off
chcp 65001 > nul
cls
echo ========================================================
echo  🌍 Shukatsu Intelligence Patrol (Manual Mode) 🌍
echo ========================================================
echo.
echo  [Info] Realtime Log Viewer
echo  [Info] Random delay (1.5-3.5s) enabled for anti-bot.
echo.
echo  📡 Patroling sources...
echo.

cd /d "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES"
python apps/MEDIA/INTELLIGENCE_HUB/shukatsu_patrol.py

echo.
echo ========================================================
echo  ✅ Patrol Complete
echo ========================================================
pause
