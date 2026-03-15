@echo off
chcp 65001 > nul
title 統合ランチャー

:MENU
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║             統合ランチャー                        ║
echo ║               メインメニュー                      ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo   [1] 全自動モード（パトロール＋壁紙監視）
echo   [2] ハブを起動
echo   [3] 情報収集パトロール
echo   [4] 壁紙ウォッチャー
echo   [5] スケジュールアーカイブ整理
echo   [6] 壁紙を今すぐ更新
echo   [7] ESアシスタント
echo   [8] SPI道場
echo   [9] 大西道場
echo   [0] 終了
echo.
set /p choice="選択してください [0-9]: "

if "%choice%"=="0" goto END
if "%choice%"=="1" goto AUTO_ALL
if "%choice%"=="2" goto EGO_HUB
if "%choice%"=="3" goto PATROL
if "%choice%"=="4" goto WALLPAPER_WATCHER
if "%choice%"=="5" goto ARCHIVE
if "%choice%"=="6" goto UPDATE_WALLPAPER
if "%choice%"=="7" goto ES_ASSISTANT
if "%choice%"=="8" goto SPI_DOJO
if "%choice%"=="9" goto ONISHI_DOJO

echo 無効な選択です
timeout /t 2 > nul
goto MENU

:AUTO_ALL
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   全自動モード起動中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

echo [1/3] 壁紙ウォッチャー起動...
start "壁紙ウォッチャー" /min python VECTIS_SYSTEM_FILES\bin\schedule_wallpaper_watcher.py

echo [2/3] 情報収集パトロール起動...
:AUTO_LOOP
echo.
echo [%date% %time%] パトロール開始...
python VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\shukatsu_patrol.py

echo.
echo [%date% %time%] パトロール完了。5分後に再実行...
echo.
timeout /t 300 > nul
goto AUTO_LOOP

:EGO_HUB
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\vectis_hub.py
goto MENU

:PATROL
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
:PATROL_LOOP
cls
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   情報収集パトロール (ループモード)
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo [%date% %time%] パトロール開始...
python VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\shukatsu_patrol.py
echo.
echo [%date% %time%] 完了。5分後に再実行...
timeout /t 300 > nul
goto PATROL_LOOP

:WALLPAPER_WATCHER
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
pip install watchdog -q
python VECTIS_SYSTEM_FILES\bin\schedule_wallpaper_watcher.py
goto MENU

:ARCHIVE
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\bin\schedule_archiver.py
echo.
pause
goto MENU

:UPDATE_WALLPAPER
cd /d "%~dp0\..\VECTIS_SYSTEM_FILES\bin"
..\..\.venv\Scripts\python.exe update_wallpaper.py
echo.
pause
goto MENU

:ES_ASSISTANT
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\CAREER\es_assistant\app.py
goto MENU

:SPI_DOJO
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\CAREER\spi_trainer\main.py
goto MENU

:ONISHI_DOJO
cd /d "%~dp0\.."
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\UTILS\onishi\study_app.py
goto MENU

:END
echo.
echo さようなら！
timeout /t 2 > nul
exit
