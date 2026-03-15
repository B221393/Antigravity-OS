@echo off
chcp 65001 >nul
title 🎤 Voice Typer v2

echo.
echo ========================================
echo   🎤 Voice Typer v2 - 音声直接入力
echo   管理者権限不要 / ffmpeg不要
echo ========================================
echo.

REM ── 多重起動防止 ──
tasklist /FI "WINDOWTITLE eq 🎤 Voice Typer v2" 2>nul | find /I "cmd.exe" >nul
if not errorlevel 1 (
    echo ⚠️  Voice Typer は既に起動しています！
    echo    既存のウィンドウを確認してください。
    echo.
    pause
    exit /b
)

REM ── 既存の voice_typer.py プロセスを停止 ──
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST 2^>nul ^| find /I "PID"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | find /I "voice_typer.py" >nul
    if not errorlevel 1 (
        echo 🔄 既存の Voice Typer プロセスを停止中...
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo 🚀 Voice Typer を起動します...
echo    [F9] 長押し → 録音 → 離す → 自動入力
echo    Ctrl+C → 終了
echo.

cd /d "%~dp0\app\python_scripts"
python voice_typer.py %*

echo.
echo 🛑 Voice Typer を終了しました。
pause
