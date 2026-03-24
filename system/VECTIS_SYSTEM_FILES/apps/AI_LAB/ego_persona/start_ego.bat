@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Ego Persona - AI Digital Twin

echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║         🧠 EGO PERSONA - Your Digital Twin                 ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo ✨ 修正完了！Text Routerとの連携が有効になりました
echo.
echo 起動中...
echo.

REM 仮想環境のStreamlitを使用
..\..\..\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8510

pause
