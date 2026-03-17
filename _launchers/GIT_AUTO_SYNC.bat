@echo off
title Git Auto-Sync
cd /d %~dp0..
echo Starting Git Auto-Sync...
python python_scripts/git_auto_sync.py
pause
