@echo off
chcp 65001
cd /d "%~dp0"
echo 🏛️ 教養チャンネル (History - Native) を起動しています...
echo.

:: 仮想環境のパス
set VENV_PATH=..\..\..\.venv

if exist "%VENV_PATH%\Scripts\python.exe" (
    "%VENV_PATH%\Scripts\python.exe" app_native.py
) else (
    echo [ERROR] 仮想環境が見つかりません。
    pause
)
