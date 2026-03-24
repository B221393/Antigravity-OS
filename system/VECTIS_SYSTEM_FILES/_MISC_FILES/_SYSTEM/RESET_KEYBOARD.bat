@echo off
setlocal
title VECTIS - EMERGENCY KEYBOARD RESET

echo ==========================================================
echo    VECTIS OS : EMERGENCY RESET (QWERTYに戻す)
echo ==========================================================
echo.
echo  [SYSTEM] 全ての AutoHotkey スクリプトを強制停止しています...

:: AutoHotkey プロセスを強制終了
taskkill /f /im AutoHotkey.exe /t >nul 2>&1

if %errorlevel% equ 0 (
    echo.
    echo  [SUCCESS] キーボード配列を QWERTY (標準) に戻しました。
) else (
    echo.
    echo  [INFO] AutoHotkey は起動していませんでした。
)

echo.
echo  3秒後にこのウィンドウを閉じます。
timeout /t 3 >nul
exit
