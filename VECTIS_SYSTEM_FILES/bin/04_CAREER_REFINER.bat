@echo off
setlocal
cd /d "%~dp0..\apps\MEDIA\INTELLIGENCE_HUB"
echo [VECTIS] Starting Career Refiner...
python career_refiner.py
echo [VECTIS] Refinement Complete.
pause
