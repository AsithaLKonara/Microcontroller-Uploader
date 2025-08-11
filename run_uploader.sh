#!/bin/bash

# J Tech Pixel Uploader Launcher Script
# For Linux and macOS

echo "Starting J Tech Pixel Uploader..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9 or higher"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

echo "Python version: $python_version"

# Check if required packages are installed
echo "Checking dependencies..."

# Check tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "Error: tkinter is not available"
    echo "Please install Python with tkinter support"
    echo "Ubuntu/Debian: sudo apt install python3-tk"
    echo "macOS: brew install python-tk"
    exit 1
fi

# Check pyserial
if ! python3 -c "import serial" &> /dev/null; then
    echo "Installing pyserial..."
    pip3 install pyserial
fi

# Check esptool
if ! python3 -c "import esptool" &> /dev/null; then
    echo "Installing esptool..."
    pip3 install esptool
fi

echo "Dependencies OK!"
echo
echo "Starting application..."
echo

# Run the application
python3 j_tech_pixel_uploader.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "Application exited with an error"
    read -p "Press Enter to continue..."
fi
