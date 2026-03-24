@echo off
chcp 65001 >nul
title 緊急 - QWERTY固定モード（シャットダウン対策）

echo.
echo ==============================================================
echo    🚨 緊急 QWERTY 固定モード 🚨
echo ==============================================================
echo.
echo このスクリプトを実行すると:
echo   1. 現在の大西配列を停止します
echo   2. AutoHotkeyのスタートアップを無効化します
echo   3. シャットダウン/再起動後もQWERTYのままになります
echo.
echo ==============================================================
echo.

:: 確認
set /p confirm="続行しますか？ (y/n): "
if /i not "%confirm%"=="y" (
    echo キャンセルしました。
    pause
    exit /b
)

echo.
echo [1/3] AutoHotkeyプロセスを終了中...
taskkill /f /im AutoHotkeyU64.exe 2>nul
taskkill /f /im AutoHotkey.exe 2>nul
echo      ✅ 完了

echo.
echo [2/3] AutoHokeyのスタートアップを無効化中...

:: スタートアップフォルダからショートカットを削除（存在する場合）
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del "%STARTUP%\onishi_layout.ahk.lnk" 2>nul
del "%STARTUP%\onishi_layout.lnk" 2>nul
del "%STARTUP%\大西配列.lnk" 2>nul
del "%STARTUP%\*.ahk" 2>nul

:: フラグファイルを作成（次回起動時に大西配列をブロック）
echo QWERTY_LOCKED > "%~dp0.qwerty_lock"
echo      ✅ 完了

echo.
echo [3/3] セーフモードフラグを設定中...
:: スタートアップ時にチェックされるフラグ
echo %date% %time% - QWERTY固定モード有効化 >> "%~dp0emergency_log.txt"
echo      ✅ 完了

echo.
echo ==============================================================
echo    ✅ QWERTY固定モードが有効になりました！
echo ==============================================================
echo.
echo  ⚠️  シャットダウン/再起動後もQWERTY配列のままです
echo.
echo  大西配列を再度使いたい場合は:
echo    → 「大西配列_復元.bat」を実行してください
echo.
echo ==============================================================
echo.
pause
