@echo off
chcp 65001 >nul
title 大西配列 復元

echo.
echo ==============================================================
echo    大西配列を復元します
echo ==============================================================
echo.

:: ロックファイルを削除
if exist "%~dp0.qwerty_lock" (
    del "%~dp0.qwerty_lock"
    echo ✅ QWERTY固定モードを解除しました
) else (
    echo ℹ️  QWERTY固定モードは有効ではありませんでした
)

echo.
echo 大西配列を開始しますか？
set /p start_now="今すぐ開始する場合は y を入力: "

if /i "%start_now%"=="y" (
    echo.
    echo 大西配列を開始中...
    start "" "%~dp0onishi_layout.ahk"
    echo ✅ 大西配列を開始しました
)

echo.
echo ==============================================================
echo    完了！
echo ==============================================================
echo.
echo  ヒント: スタートアップに登録したい場合は
echo         onishi_layout.ahk のショートカットを
echo         %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo         に配置してください
echo.
echo ==============================================================

:: ログ記録
echo %date% %time% - 大西配列を復元 >> "%~dp0emergency_log.txt"

pause
