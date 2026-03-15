@echo off
chcp 65001 > nul
echo ============================================
echo 🔄 スキップ動画リトライ
echo ============================================
echo.

cd /d "%~dp0"

if not exist skipped_videos.log (
    echo ⚠️ skipped_videos.log が見つかりません。
    pause
    exit /b
)

echo 📋 スキップされた動画一覧:
echo.
type skipped_videos.log
echo.
echo ============================================
echo.

set /p confirm=🔄 これらの動画を再処理しますか？ (y/N): 

if /i not "%confirm%"=="y" (
    echo ⏭️ キャンセルしました。
    pause
    exit /b
)

echo.
echo 🚀 リトライ中...

:: ログからVIDを抽出してAUTO_YOUTUBE.txtに追加
for /f "tokens=3 delims=|" %%v in (skipped_videos.log) do (
    echo https://www.youtube.com/watch?v=%%v >> AUTO_YOUTUBE.txt
)

echo.
echo ✅ AUTO_YOUTUBE.txt にURLを追加しました。
echo    次回のWatcher実行で処理されます。
echo.

:: ログをクリア
del skipped_videos.log 2>nul
echo 🗑️ skipped_videos.log をクリアしました。

pause
