@echo off
chcp 65001 > nul
title ⚡ VECTIS 全自動オペレーション ⚡

:LOOP
cls
echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║       ⚡ VECTIS 全自動オペレーション ⚡              ║
echo ║                                                   ║
echo ║   システムを自動巡回し、常に最新状態を維持します     ║
echo ╚═══════════════════════════════════════════════════╝
echo.
echo [Time] %date% %time%
echo.

echo 🔄 [1/3] 📡 情報収集パトロール (Shukatsu Patrol)
cd /d "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES"
python apps/MEDIA/INTELLIGENCE_HUB/shukatsu_patrol.py

echo.
echo 🔄 [2/3] 📅 スケジュール・壁紙同期 (Wallpaper Sync)
python bin/schedule_wallpaper_watcher.py --once

echo.
echo 🔄 [3/3] 📊 統計データ更新 (Stats Update)
python bin/collection_stats.py --silent

echo.
echo ✅ サイクル完了。待機モードに入ります... (60秒)
echo ☕ 現在のステータス: 正常 (System Green)
echo.
timeout /t 60 > nul
goto LOOP
