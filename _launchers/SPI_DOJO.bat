@echo off
chcp 65001 >nul
title SPI DOJO

cd /d "%~dp0\..\VECTIS_SYSTEM_FILES"
..\.venv\Scripts\python.exe apps\CAREER\spi_trainer\main.py

pause
