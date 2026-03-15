@echo off
setlocal
cd /d "%~dp0"

:: 仮想環境のPythonを使用して起動
if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\pythonw.exe" "START_PRACTICE.py"
) else (
    :: 仮想環境がない場合はシステムPythonを使用
    start "" pythonw "START_PRACTICE.py"
)

exit
