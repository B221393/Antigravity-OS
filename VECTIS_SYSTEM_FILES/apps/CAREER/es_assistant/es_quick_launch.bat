@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ES ASSISTANT - Quick Launch
color 0B

:menu
cls
echo ╔════════════════════════════════════════╗
echo ║   ES ASSISTANT - Quick Launch 📝       ║
echo ╚════════════════════════════════════════╝
echo.
echo  [1] 📄 新しいESを作成
echo  [2] 📋 Draftsフォルダを開く
echo  [3] 🎯 Targeted ESを開く
echo  [4] 📊 ES一覧を表示
echo  [5] 🚀 ES Assistant GUI起動 (Streamlit)
echo  [6] 🔍 最新のESを編集
echo  [7] 📂 フォルダ整理
echo  [0] ❌ 終了
echo.
set /p choice="選択してください (0-7): "

if "%choice%"=="1" goto create_new
if "%choice%"=="2" goto open_drafts
if "%choice%"=="3" goto open_targeted
if "%choice%"=="4" goto view_all
if "%choice%"=="5" goto launch_gui
if "%choice%"=="6" goto edit_latest
if "%choice%"=="7" goto organize
if "%choice%"=="0" goto end

echo 無効な選択です。
timeout /t 2 >nul
goto menu

:create_new
cls
echo ╔════════════════════════════════════════╗
echo ║     新しいES作成 📄                     ║
echo ╚════════════════════════════════════════╝
echo.
set /p company="企業名を入力: "
if "%company%"=="" goto menu

set timestamp=%date:~0,4%%date:~5,2%%date:~8,2%
set filename=draft_%timestamp%_%company%.md

echo # ES Draft: %company% > "drafts\%filename%"
echo. >> "drafts\%filename%"
echo Created: %date% %time% >> "drafts\%filename%"
echo. >> "drafts\%filename%"
echo ## 志望動機 >> "drafts\%filename%"
echo. >> "drafts\%filename%"
echo ## 自己PR >> "drafts\%filename%"
echo. >> "drafts\%filename%"
echo ## 学生時代に力を入れたこと >> "drafts\%filename%"
echo. >> "drafts\%filename%"

echo.
echo ✅ 作成完了: %filename%
echo.
echo [1] 今すぐ編集
echo [2] メニューに戻る
set /p edit_choice="選択: "
if "%edit_choice%"=="1" notepad "drafts\%filename%"
goto menu

:open_drafts
explorer "drafts"
goto menu

:open_targeted
cls
echo ╔════════════════════════════════════════╗
echo ║    ターゲット企業ES 🎯                  ║
echo ╚════════════════════════════════════════╝
echo.
dir /b "drafts_targeted\*.md" 2>nul
echo.
set /p target="開くファイル名を入力: "
if exist "drafts_targeted\%target%" (
    notepad "drafts_targeted\%target%"
) else (
    echo ❌ エラー: ファイルが見つかりません
    timeout /t 2 >nul
)
goto menu

:view_all
cls
echo ╔════════════════════════════════════════╗
echo ║      ES一覧 📊                          ║
echo ╚════════════════════════════════════════╝
echo.
echo 📂 Drafts:
dir /b "drafts\*.md" 2>nul | find /c /v "" > temp.txt
set /p count=<temp.txt
del temp.txt
echo   合計: %count% 件
dir /b "drafts\*.md" 2>nul
echo.
echo 📂 Targeted:
dir /b "drafts_targeted\*.md" 2>nul | find /c /v "" > temp.txt
set /p count2=<temp.txt
del temp.txt
echo   合計: %count2% 件
dir /b "drafts_targeted\*.md" 2>nul
echo.
pause
goto menu

:launch_gui
cls
echo 🚀 ES Assistant GUI (Streamlit) を起動中...
echo.
call "..\..\..\.venv\Scripts\activate.bat"
streamlit run app.py
echo.
echo ⚠️ 画面が閉じたりエラーが出た場合は、開発者(ログ)を確認してください。
pause
goto menu

:edit_latest
cls
echo 🔍 最新のESを検索中...
for /f "delims=" %%f in ('dir /b /o-d "drafts\*.md" 2^>nul') do (
    set latest=%%f
    goto found_latest
)
echo ❌ ESが見つかりません
timeout /t 2 >nul
goto menu

:found_latest
echo ✅ 最新: %latest%
notepad "drafts\%latest%"
goto menu

:organize
cls
echo ╔════════════════════════════════════════╗
echo ║    フォルダ整理 📂                      ║
echo ╚════════════════════════════════════════╝
echo.
echo 必要なフォルダを作成中...
if not exist "drafts" mkdir "drafts"
if not exist "drafts_targeted" mkdir "drafts_targeted"
if not exist "templates" mkdir "templates"
if not exist "archive" mkdir "archive"
echo ✅ 完了しました
timeout /t 2 >nul
goto menu

:end
cls
echo 👋 終了します。
timeout /t 1 >nul
exit
