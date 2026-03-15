@echo off
echo [INFO] Fetching latest schedule from Google Calendar...
python "C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\UTILS\calendar\google_calendar_client.py"

echo.
echo [INFO] Updating tasks.md with the new schedule...
python "C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\scripts\update_tasks_md.py"

echo.
echo [INFO] Updating Desktop Wallpaper...
python "C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\scripts\update_wallpaper.py"

echo.
echo [SUCCESS] Schedule and Wallpaper update process completed.
timeout /t 5
