@echo off
chcp 65001 >nul
title QWERTY復元

echo ==========================================================
echo    大西配列を停止してQWERTY配列に戻します
echo ==========================================================
echo.

:: AutoHotkeyプロセスを終了
taskkill /f /im AutoHotkeyU64.exe 2>nul
taskkill /f /im AutoHotkey.exe 2>nul

echo.
echo ✅ 完了！キーボードはQWERTY配列に戻りました。
echo.
echo ----------------------------------------------------------
echo  再度大西配列を有効にするには:
echo  onishi_layout.ahk をダブルクリック
echo ----------------------------------------------------------
echo.
pause
