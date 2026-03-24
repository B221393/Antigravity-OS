@echo off
chcp 65001 > nul
title 🤖 AIゲートウェイ (Moltbot)

echo.
echo ╔═══════════════════════════════════════╗
echo ║       AIゲートウェイ 起動中...        ║
echo ║         Moltbot ローカルモード        ║
echo ╚═══════════════════════════════════════╝
echo.

echo 📡 Moltbot ゲートウェイを起動します...
echo    (Ollamaが起動していることを確認してください)
echo.

call moltbot gateway

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ エラー: Moltbot の起動に失敗しました
    echo    → moltbot がインストールされていない可能性があります
    echo    → npm install -g moltbot を実行してください
)

pause
