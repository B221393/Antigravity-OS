@echo off
chcp 65001 >nul
cd /d "%~dp0"
title CHAT ANALYZER - 会話解析ツール
pythonw app.py
