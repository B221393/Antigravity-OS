@echo off
setlocal
cd /d "%~dp0"
:: Pythonの仮想環境があればそれを使用、なければシステム標準のpythonを使用
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe VECTIS_SYSTEM_FILES\apps\AI_LAB\local_brain\brain.py
) else (
    python VECTIS_SYSTEM_FILES\apps\AI_LAB\local_brain\brain.py
)
pause
