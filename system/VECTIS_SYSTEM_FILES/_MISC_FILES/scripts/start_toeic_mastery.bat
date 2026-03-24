@echo off
setlocal
echo ==================================================
echo   TOEICマスタリーAI - アプリを起動しています
echo ==================================================
echo.
echo 1. サーバーの準備を確認中...
cd /d "%~dp0\apps\toeic_mastery"

echo 2. アプリを起動します (npm run dev)
echo ブラウザが自動的に開かない場合は、以下のURLにアクセスしてください:
echo http://localhost:3000
echo.
echo ※終了するには、この画面で CTRL+C を押してください
echo.

:: ブラウザを開く (少し待ってから)
start http://localhost:3000

:: サーバー起動
npm run dev
pause
