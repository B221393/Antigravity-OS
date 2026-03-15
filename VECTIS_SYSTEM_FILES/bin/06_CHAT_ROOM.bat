@echo off
setlocal
cd /d "%~dp0"
title CHAT ANALYZER
:: The user wants an interactive chat. 'pythonw' suppresses the console window.
:: We must use 'python' to allow typing in the chat.
call .venv\Scripts\activate

:: Try to find the chat app
if exist "VECTIS_SYSTEM_FILES\apps\AI_LAB\chat_analyzer\app.py" (
    python "VECTIS_SYSTEM_FILES\apps\AI_LAB\chat_analyzer\app.py"
) else (
    echo [ERROR] Chat app not found. Searching...
    :: Fallback search or typical location
    python "VECTIS_SYSTEM_FILES\apps\chat_analyzer\app.py"
)
pause
