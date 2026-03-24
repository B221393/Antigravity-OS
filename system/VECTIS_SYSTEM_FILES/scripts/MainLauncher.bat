@echo off
chcp 65001 > nul
title VECTIS メインランチャー

:MENU
cls
echo.
echo ╔════════════════════════════════════════════════════╗
echo ║           VECTIS メインランチャー                  ║
echo ║               メインメニュー                        ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo   [1] 🚀 全自動モード（推奨）
echo   [2] 📊 VECTISハブ
echo   [3] 🔍 情報収集パトロール
echo   [4] 🖼️  壁紙メニュー
echo   [5] 📅 スケジュール管理
echo   [6] 🎮 ゲーム＆リラックス
echo   [7] 🎨 クリエイティブツール
echo   [8] 📝 就活支援ツール
echo   [9] 🌌 全アプリブラウザ (100+個)
echo   [S] 📈 収集統計を表示
echo   [0] ❌ 終了
echo.
set /p choice="選択してください: "

if "%choice%"=="0" goto END
if "%choice%"=="1" goto AUTO_ALL
if "%choice%"=="2" goto VECTIS_HUB
if "%choice%"=="3" goto PATROL
if "%choice%"=="4" goto WALLPAPER_MENU
if "%choice%"=="5" goto SCHEDULE_MENU
if "%choice%"=="6" goto GAMES_MENU
if "%choice%"=="7" goto CREATIVE_MENU
if "%choice%"=="8" goto CAREER_MENU
if "%choice%"=="9" goto APP_BROWSER
if /i "%choice%"=="S" goto STATS

echo 無効な選択です
timeout /t 2 > nul
goto MENU

:WALLPAPER_MENU
cls
echo.
echo ╔════════ 壁紙メニュー ════════╗
echo   [1] ウォッチャー起動 (自動更新)
echo   [2] 今すぐ壁紙を更新
echo   [3] 戻る
echo.
set /p wp_choice="選択: "
if "%wp_choice%"=="1" goto WALLPAPER_WATCHER
if "%wp_choice%"=="2" goto UPDATE_WALLPAPER
if "%wp_choice%"=="3" goto MENU
goto WALLPAPER_MENU

:SCHEDULE_MENU
cls
echo.
echo ╔════════ スケジュール ════════╗
echo   [1] アーカイブ整理 (過去イベント移動)
echo   [2] 直近の予定を確認 (SCHEDULE.md)
echo   [3] 戻る
echo.
set /p sc_choice="選択: "
if "%sc_choice%"=="1" goto ARCHIVE
if "%sc_choice%"=="2" (
    start notepad "VECTIS_SYSTEM_FILES\CAREER\SCHEDULE.md"
    goto MENU
)
if "%sc_choice%"=="3" goto MENU
goto SCHEDULE_MENU

:GAMES_MENU
cls
echo.
echo ╔════════ ゲーム＆リラックス ════════╗
echo   [1] 💣 DT Cannon (ストレス発散)
echo   [2] ⌨️  タイピングテスト
echo   [3] 🏯 Knowledge Spire (タワーディフェンス)
echo   [4] 🎈 Fun Zone
echo   [5] 戻る
echo.
set /p gm_choice="選択: "
if "%gm_choice%"=="1" goto DTCANNON
if "%gm_choice%"=="2" goto TYPING
if "%gm_choice%"=="3" goto SPIRE
if "%gm_choice%"=="4" goto FUNZONE
if "%gm_choice%"=="5" goto MENU
goto GAMES_MENU

:CREATIVE_MENU
cls
echo.
echo ╔════════ クリエイティブ ════════╗
echo   [1] 🎨 Color Alchemy (パレット生成)
echo   [2] 🖼️  ASCII Artist (画像変換)
echo   [3] 🔊 FX Soundboard (集中サウンド)
echo   [4] 📉 Image Diet (画像圧縮)
echo   [5] 📄 PDF Splicer (結合・分割)
echo   [6] 🎥 Video Studio (動画台本作成)
echo   [7] 戻る
echo.
set /p cr_choice="選択: "
if "%cr_choice%"=="1" goto COLOR_ALCHEMY
if "%cr_choice%"=="2" goto ASCII_ARTIST
if "%cr_choice%"=="3" goto SOUNDBOARD
if "%cr_choice%"=="4" goto IMAGE_DIET
if "%cr_choice%"=="5" goto PDF_SPLICER
if "%cr_choice%"=="6" goto VIDEO_STUDIO
if "%cr_choice%"=="7" goto MENU
goto CREATIVE_MENU

:CAREER_MENU
cls
echo.
echo ╔════════ 就活支援 ════════╗
echo   [1] 📝 ESアシスタント
echo   [2] 🧠 SPI道場
echo   [3] 💬 大西道場 (面接)
echo   [4] ♟️  将棋道場 (AI_LAB)
echo   [5] 🔬 深層分析 (Deep Analyzer)
echo   [6] 📢 情報分析ブリーフィング (博士と助手)
echo   [7] 戻る
echo.
set /p ca_choice="選択: "
if "%ca_choice%"=="1" goto ES_ASSISTANT
if "%ca_choice%"=="2" goto SPI_DOJO
if "%ca_choice%"=="3" goto ONISHI_DOJO
if "%ca_choice%"=="4" goto SHOGI_DOJO
if "%ca_choice%"=="5" goto DEEP_ANALYZER
if "%ca_choice%"=="6" goto BRIEFING
if "%ca_choice%"=="7" goto MENU
goto CAREER_MENU

:: --- Action Blocks ---

:APP_BROWSER
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\bin\apps_browser.py
goto MENU

:DEEP_ANALYZER
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\AI_LAB\deep_analyzer\app.py
goto MENU

:BRIEFING
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\briefing.py
goto MENU

:VIDEO_STUDIO
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\video_studio\app.py
goto MENU

:DTCANNON
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\GAMES\dt_cannon\dt_cannon.py
goto MENU

:TYPING
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\GAMES\typing_test\typing_test.py
goto MENU

:SPIRE
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\GAMES\knowledge_spire\game.py
goto MENU

:FUNZONE
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\GAMES\fun_zone\app.py
goto MENU

:COLOR_ALCHEMY
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\color_alchemy\app.py
goto MENU

:ASCII_ARTIST
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\ascii_artist\app.py
goto MENU

:SOUNDBOARD
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\fx_soundboard\app.py
goto MENU

:IMAGE_DIET
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\image_diet\app.py
goto MENU

:PDF_SPLICER
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\MEDIA\pdf_splicer\app.py
goto MENU

:ES_ASSISTANT
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\AI_LAB\es_assistant\app.py
goto MENU

:SPI_DOJO
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\BIZ\spi_dojo\app.py
goto MENU

:ONISHI_DOJO
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\BIZ\onishi_dojo\app.py
goto MENU

:SHOGI_DOJO
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\apps\AI_LAB\shogi_dojo\app.py
goto MENU

:AUTO_ALL
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   🚀 全自動モードを起動中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
if exist "c:\Users\Yuto\Desktop\⚡全自動モード起動.bat" (
    call "c:\Users\Yuto\Desktop\⚡全自動モード起動.bat"
) else (
    echo [ERROR] 全自動起動スクリプトが見つかりません
    pause
)
goto MENU

:VECTIS_HUB
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   VECTISハブを起動中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
start "" python VECTIS_SYSTEM_FILES\vectis_hub.py
goto MENU

:PATROL
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   情報収集パトロールを起動中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
start "" python VECTIS_SYSTEM_FILES\apps\MEDIA\INTELLIGENCE_HUB\shukatsu_patrol.py
goto MENU

:WALLPAPER_WATCHER
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   壁紙ウォッチャーを起動中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
pip install watchdog -q
start "" /min python VECTIS_SYSTEM_FILES\bin\schedule_wallpaper_watcher.py
goto MENU

:ARCHIVE
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   アーカイブ整理中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\bin\schedule_archiver.py
pause
goto MENU

:UPDATE_WALLPAPER
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   壁紙を手動更新中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\bin\update_wallpaper.py
echo.
echo 更新完了！デスクトップを確認してください。
pause
goto MENU

:STATS
cls
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo   収集統計を計算中...
echo ━━━━━━━━━━━━━━━━━━━━━━━━
echo.
cd /d "c:\Users\Yuto\Desktop\app"
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python VECTIS_SYSTEM_FILES\bin\collection_stats.py
echo.
pause
goto MENU

:END
exit
