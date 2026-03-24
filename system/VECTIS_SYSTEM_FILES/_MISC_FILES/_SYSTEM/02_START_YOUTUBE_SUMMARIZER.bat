@echo off
setlocal
chcp 65001 >nul
title [START] YouTube 要約 AI
cls

echo ==========================================================
echo    START : YouTube 要約 AI (Gemini 2.0)
echo ==========================================================
echo.
echo  機能:
echo  1. YouTube URLから動画を自動要約
echo  2. Gemini 2.0 による高品質な日本語要約
echo  3. 要約履歴の保存・管理
echo  4. テキストファイルへのエクスポート
echo.
echo ----------------------------------------------------------
echo  サーバーを起動しています... (Port: 5174)
echo ----------------------------------------------------------

cd /d "%~dp0apps\youtube_summarizer"

:: ブラウザで自動的に開く
start http://localhost:5174

:: 開発用サーバー起動
npm run dev -- --port 5174

pause
