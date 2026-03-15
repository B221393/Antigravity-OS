@echo off
:: Antigravity Daily Log - 自動更新＆NotebookLMアップロード
:: スタートアップから毎朝実行

set PYTHON=C:\Users\Yuto\Desktop\app\.venv\Scripts\python.exe
set SCRIPT=C:\Users\Yuto\Desktop\app\daily_log.py
set PYTHONUTF8=1

:: 少し待つ（ネットワーク接続を待つため）
timeout /t 15 /nobreak > nul

:: ログ追記 ＋ NotebookLMに自動アップロード
"%PYTHON%" "%SCRIPT%" --upload > nul 2>&1
