@echo off
title J Tech Pixel Uploader
echo Starting J Tech Pixel Uploader...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Error: tkinter is not available
    echo Please install Python with tkinter support
    pause
    exit /b 1
)

python -c "import serial" >nul 2>&1
if errorlevel 1 (
    echo Installing pyserial...
    pip install pyserial
)

python -c "import esptool" >nul 2>&1
if errorlevel 1 (
    echo Installing esptool...
    pip install esptool
)

echo Dependencies OK!
echo.
echo Starting application...
echo.

REM Run the application
python j_tech_pixel_uploader.py

REM If there's an error, pause to show the message
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
