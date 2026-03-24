@echo off
:: Use UTF-8 for Japanese character support in CMD
chcp 65001 >nul
setlocal enabledelayedexpansion
title VECTIS OS - 統合スタートメニュー
cls

:menu
cls
echo ==========================================================
echo    VECTIS OS : INTEGRATED ROADS (統合スタートメニュー)
echo ==========================================================
echo.
echo  [D] 総合ポータル HUB (Netflix-style UI)
echo      - 全ての機能への集約ハブ (Port 8501-8504統制)
echo.
echo  [1] TOEIC Mastery AI (Port 8502)
echo      - AI試験 / 990点診断
echo.
echo  [2] Onishi Typing / Job Hunter (Port 8501)
echo      - タイピング練習 / 就活 / 3Dマップ
echo.
echo  [3] System Monitor / Log (Port 8504)
echo      - APIコスト / 音声記録 / ログ
echo.
echo  [4] AI Life Diary (Port 8503)
echo.
echo  [5] 日本史・教養学習 (Port 8505)
echo.
echo  [6] YouTube要約AI (Port 5174)
echo      - YouTube動画をAIで自動要約
echo.
echo  [0] 終了
echo.
echo ----------------------------------------------------------
set /p choice="番号を入力して [ENTER] を押してください: "

if /i "%choice%"=="D" goto start_all
if "%choice%"=="1" goto start_toeic
if "%choice%"=="2" goto start_job
if "%choice%"=="3" goto start_monitor
if "%choice%"=="4" goto start_diary
if "%choice%"=="5" goto start_history
if "%choice%"=="6" goto start_youtube
if "%choice%"=="0" exit
goto menu

:start_all
echo VECTISエコシステムを起動中...
start "VECTIS_OS" cmd /c "cd /d %~dp0apps\job_hunting && python -m streamlit run dashboard.py --server.port 8501"
start "VECTIS_OS" cmd /c "cd /d %~dp0apps\toeic && python -m streamlit run app.py --server.port 8502"
start "VECTIS_OS" cmd /c "cd /d %~dp0apps\diary && python -m streamlit run app.py --server.port 8503"
start "VECTIS_OS" cmd /c "cd /d %~dp0apps\system_monitor && python -m streamlit run app.py --server.port 8504"
start "VECTIS_OS" cmd /c "cd /d %~dp0apps\history && python -m streamlit run app.py --server.port 8505"
timeout /t 5
start "" "%~dp0apps\dashboard\index.html"
goto menu

:start_toeic
echo TOEICアプリを起動中...
start cmd /c "cd /d %~dp0apps\toeic && python -m streamlit run app.py --server.port 8502"
goto menu

:start_job
echo Job Hunter / Onishi を起動中...
start cmd /c "cd /d %~dp0apps\job_hunting && python -m streamlit run dashboard.py --server.port 8501"
goto menu

:start_monitor
echo システムモニターを起動中...
start cmd /c "cd /d %~dp0apps\system_monitor && python -m streamlit run app.py --server.port 8504"
goto menu

:start_diary
echo 日記アプリを起動中...
start cmd /c "cd /d %~dp0apps\diary && python -m streamlit run app.py --server.port 8503"
goto menu

:start_history
echo 歴史学習アプリを起動中...
start cmd /c "cd /d %~dp0apps\history && python -m streamlit run app.py --server.port 8505"
goto menu

:start_youtube
echo YouTube要約AIを起動中...
start cmd /c "cd /d %~dp0apps\youtube_summarizer && npm run dev -- --port 5174"
start http://localhost:5174
goto menu
