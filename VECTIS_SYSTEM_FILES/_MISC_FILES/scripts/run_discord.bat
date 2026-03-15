@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Starting VECTIS REMOTE LINK...
python apps\discord_bot\bot.py
pause
