@echo off
chcp 65001 > nul
title 🤖 Moshi Voice Server 🤖

echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║          🤖 Moshi Voice AI Server 🤖              ║
echo ║                                                   ║
echo ║  iOS等のクライアントから接続するためのサーバーです  ║
echo ╚═══════════════════════════════════════════════════╝
echo.

cd /d "c:\Users\Yuto\Desktop\app"

:: 仮想環境の有効化
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Python仮想環境(.venv)が見つかりません。
    pause
    exit /b
)

echo 📦 Moshiをインストール/更新しています...
pip install -U moshi
cls

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  📡 接続情報 (IP Address)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo  iPhoneから接続する際は、以下のIPアドレスを使用してください:
echo.
ipconfig | findstr "IPv4"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🚀 Moshiサーバーを起動します...
echo    接続先URL: http://[上記のIPアドレス]:8998
echo.
echo    (終了するには Ctrl+C を押してください)
echo.

python -m moshi.server --host 0.0.0.0 --port 8998

pause
