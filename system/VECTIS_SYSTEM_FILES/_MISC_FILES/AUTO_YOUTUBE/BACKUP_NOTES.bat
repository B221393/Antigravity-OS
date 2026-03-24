@echo off
title 📂 Backup YouTube Notes
echo.
echo  =======================================================
echo   Backing up YouTube Summaries...
echo  =======================================================
echo.

set SRC="..\apps\memory\data\youtube_notes"
set DST="%USERPROFILE%\Desktop\VECTIS_YouTube_Notes"

if not exist %DST% mkdir %DST%

xcopy %SRC%\*.md %DST% /D /Y

echo.
echo  ✅ Copied all new notes to Desktop/VECTIS_YouTube_Notes
echo.
pause
