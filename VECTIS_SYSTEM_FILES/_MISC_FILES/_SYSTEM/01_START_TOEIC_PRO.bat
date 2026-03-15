@echo off
setlocal
title [START] VECTIS TOEIC PRO
cls

echo ==========================================================
echo    START : VECTIS TOEIC PRO (AI 攻略完全版)
echo ==========================================================
echo.
echo  [SYSTEM] Checking Virtual Environment...

:: 仮想環境のパスを確認
set VENV_PATH=%~dp0.venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

if exist "%PYTHON_EXE%" (
    echo  [SYSTEM] Using Virtual Environment (.venv)
    set PY_CMD="%PYTHON_EXE%"
) else (
    echo  [WARNING] Virtual Environment not found. Using system Python.
    set PY_CMD=python
)

echo.
echo ----------------------------------------------------------
echo  [SERVER] Starting Streamlit...
echo ----------------------------------------------------------
echo.

:: Streamlit 起動
%PY_CMD% -m streamlit run apps/toeic/app.py --server.headless true --browser.gatherUsageStats false

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] 起動に失敗しました。
    echo 依存ライブラリをインストールします...
    %PY_CMD% -m pip install google-generativeai gTTS streamlit python-dotenv
    echo.
    echo 再度起動を試みます...
    %PY_CMD% -m streamlit run apps/toeic/app.py --server.headless true --browser.gatherUsageStats false
)

pause
