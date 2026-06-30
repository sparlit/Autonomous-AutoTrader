@echo off
SETLOCAL EnableDelayedExpansion

echo.
echo 🌌 PHOENIX GAUNTLET V3.3.0-ASCENDANT
echo ====================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+
    pause
    goto :eof
)

python aat.py setup

echo.
echo ====================================
echo ✅ INSTALLATION COMPLETE
echo Run 'START_AAT.bat' to launch.
echo ====================================
echo.
pause
