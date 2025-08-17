@echo off
echo ========================================
echo J Tech Pixel Uploader v2.0 - Enhanced
echo ========================================
echo.
echo Starting enhanced uploader with all features...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter, serial" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pyserial esptool
)

REM Check for optional tools
echo.
echo Checking for optional tools...
python -c "import utils; utils.check_available_tools()" 2>nul
if errorlevel 1 (
    echo Some optional tools may be missing
    echo See README_ENHANCED.md for installation instructions
)

echo.
echo Starting application...
echo.

REM Run the enhanced uploader
python main.py

echo.
echo Application closed.
pause
