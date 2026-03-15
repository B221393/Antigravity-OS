@echo off
title VECTIS - Playwright Setup
color 0a
echo ===================================================
echo   VECTIS INTELLIGENCE: UPGRADING VISUAL CORTEX
echo ===================================================
echo.
echo [1/2] Installing Playwright Python Library...
pip install playwright
echo.
echo [2/2] Installing Browser Binaries (Chromium)...
python -m playwright install chromium
echo.
echo ===================================================
echo   UPGRADE COMPLETE. RESTART VECTIS OMNI.
echo ===================================================
pause
