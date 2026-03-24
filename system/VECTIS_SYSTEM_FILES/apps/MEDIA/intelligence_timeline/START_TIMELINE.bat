@echo off
echo ========================================
echo   VECTIS Intelligence Timeline
echo   3D Universe Visualizer
echo ========================================
echo.

cd /d "%~dp0"

echo Starting local server...
start "" http://localhost:8080/VECTIS_SYSTEM_FILES/apps/MEDIA/intelligence_timeline/index.html

cd /d "C:\Users\Yuto\Desktop\app"
python -m http.server 8080
