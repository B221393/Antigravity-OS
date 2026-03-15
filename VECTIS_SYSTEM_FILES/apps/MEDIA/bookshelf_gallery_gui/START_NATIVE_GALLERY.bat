@echo off
title EGO VISUAL ARCHIVE (NATIVE)
cd /d "%~dp0"
:: Activate Venv from root
:: Assuming relative path to root: ../../../../
call ..\..\..\..\.venv\Scripts\activate

python app_native.py
pause
