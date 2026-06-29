@echo off
SETLOCAL EnableDelayedExpansion

:: 16000: Phoenix Gauntlet One-Click Bootstrap
echo.
echo 🌌 PHOENIX GAUNTLET V3.3.0-ASCENDANT
echo ====================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+
    pause
    exit /b 1
)

:: Create Virtual Environment
if not exist "venv" (
    echo [1/4] Creating Virtual Environment...
    python -m venv venv
) else (
    echo [1/4] VEnv already exists.
)

:: Install Dependencies
echo [2/4] Installing Python Dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
pip install maturin pywin32 cryptography pandas psutil ujson aiosqlite fastapi uvicorn websockets dearpygui

:: Compile Rust Kernel
echo [3/4] Compiling Institutional Rust Kernel...
if exist "src\rust_institutional_core" (
    cd src\rust_institutional_core
    maturin develop --release
    cd ..\..
) else (
    echo [SKIP] Rust core directory not found.
)

:: Pre-compile Python
echo [4/4] Pre-compiling Bytecode...
python pre_compile.py

echo.
echo ====================================
echo ✅ INSTALLATION COMPLETE
echo Run 'START_AAT.bat' to launch.
echo ====================================
echo.
pause
