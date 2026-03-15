@echo off
chcp 65001 >nul
title 🎤 Voice Typer v2
echo.
echo ========================================
echo   Voice Typer v2 - 音声直接入力
echo   管理者権限不要 / ffmpeg不要
echo ========================================
echo.
cd /d "%~dp0\python_scripts"
python voice_typer.py %*
pause
