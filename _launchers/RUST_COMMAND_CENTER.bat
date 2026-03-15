@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title EGO LOW-LEVEL RUST COMMAND CENTER

:MENU
cls
echo ========================================================
echo   EGO LOW-LEVEL RUST COMMAND CENTER
echo   [RUST CORE PROJECTS LAUNCHER]
echo ========================================================
echo.
echo   [1] 🏎️  AI Racing Evolution (Genetic Algorithm)
echo   [2] ☗  Shogi Engine (Deep Learning / Bitboard)
echo   [3] 🔀  Simulate Router (Text Analysis)
echo   [4] 🚉  EGO Station (System Monitor & Backend)
echo.
echo   [E] Exit
echo.
echo ========================================================
set /p CHOICE="Selection >> "

if /i "%CHOICE%"=="1" goto RUN_RACING
if /i "%CHOICE%"=="2" goto RUN_SHOGI
if /i "%CHOICE%"=="3" goto RUN_ROUTER
if /i "%CHOICE%"=="4" goto RUN_STATION
if /i "%CHOICE%"=="E" goto END

goto MENU

:RUN_RACING
cls
echo Launching AI Racing Evolution...
echo Path: RUST_PROJECTS\racing_ai_rs
cd /d "%~dp0RUST_PROJECTS\racing_ai_rs"
cargo run --release
pause
goto MENU

:RUN_SHOGI
cls
echo Launching Shogi Engine...
echo Path: shogi_engine_rs
:: Check if it's in RUST_PROJECTS or Root (fallback)
if exist "%~dp0RUST_PROJECTS\shogi_engine_rs" (
    cd /d "%~dp0RUST_PROJECTS\shogi_engine_rs"
) else (
    cd /d "%~dp0shogi_engine_rs"
)
cargo run --release
pause
goto MENU

:RUN_ROUTER
cls
echo Launching Simulate Router...
echo Path: RUST_PROJECTS\simulate_router_rs
cd /d "%~dp0RUST_PROJECTS\simulate_router_rs"
cargo run --release
pause
goto MENU

:RUN_STATION
cls
echo Launching EGO Station Backend...
echo Path: RUST_PROJECTS\vectis-station-rs\src-tauri
cd /d "%~dp0RUST_PROJECTS\vectis-station-rs\src-tauri"
cargo run
pause
goto MENU

:END
exit
