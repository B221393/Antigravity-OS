@echo off
chcp 65001 > nul
title 📝 ES推敲テンプレート

echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║          汎用 ES ブラッシュアップ                 ║
echo ║                                                   ║
echo ║  ※このファイルをコピーして使用してください       ║
echo ║  ※下の設定エリアを書き換えてください             ║
echo ╚═══════════════════════════════════════════════════╝
echo.

:: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
:: 設定エリア（ここを変更してください）
:: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
set COMPANY_NAME=TOYOTA
set ES_FILE_PATH=C:\Users\Yuto\Documents\TOYOTA_ES.md
:: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo 企業名: %COMPANY_NAME%
echo ファイル: %ES_FILE_PATH%
echo.

cd /d "C:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

echo 🚀 ES推敲を開始します...
python VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\universal_es_refiner.py --company "%COMPANY_NAME%" --path "%ES_FILE_PATH%"

echo.
pause
