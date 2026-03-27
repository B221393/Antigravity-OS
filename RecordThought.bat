@echo off
setlocal
cd /d "%~dp0"
echo [ANTIGRAVITY] 思考の音声資産化エンジンを起動します...
echo ---------------------------------------------------------
python python_scripts\soul_voice_local.py
echo ---------------------------------------------------------
echo 資産化が完了しました。資産庫を開きます...
start "" "c:\Users\Yuto\Desktop\app\logs\ASSET_VAULT.md"
pause
