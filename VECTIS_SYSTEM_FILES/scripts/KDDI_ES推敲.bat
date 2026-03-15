@echo off
chcp 65001 > nul
title 📝 KDDI ES推敲

echo.
echo ╔═══════════════════════════════════════╗
echo ║     KDDI ES ブラッシュアップ          ║
echo ║        超高速推敲キャノン             ║
echo ╚═══════════════════════════════════════╝
echo.

cd /d "C:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

echo 🚀 KDDI向けES推敲を開始します...
python VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\universal_es_refiner.py --company "KDDI" --path "VECTIS_SYSTEM_FILES\CAREER\KDDI_ES_FINAL.md"

echo.
pause
