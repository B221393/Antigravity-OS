@echo off
chcp 65001 >nul
cd /d "%~dp0"
title TEXT ROUTER - 文章仕分け装置
pythonw app.py
