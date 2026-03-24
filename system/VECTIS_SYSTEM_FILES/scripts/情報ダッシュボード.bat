@echo off
chcp 65001 > nul
title 📊 インテリジェンス・ダッシュボード 📊

echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║    📊 インテリジェンス・ダッシュボード 📊         ║
echo ║                                                   ║
echo ║       現在の収集状況と統計データを表示します      ║
echo ╚═══════════════════════════════════════════════════╝
echo.

cd /d "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES"
python bin/collection_stats.py

echo.
echo ✅ 統計更新完了
pause
