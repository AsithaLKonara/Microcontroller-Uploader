@echo off
echo ========================================
echo Building J Tech Pixel Uploader v2.0 Final
echo ========================================
echo.

echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo Building with PyInstaller...
pyinstaller --clean --onefile --windowed --name "J_Tech_Pixel_Uploader_v2.0_Final" ^
    --add-data "config.py;." ^
    --add-data "utils.py;." ^
    --add-data "SampleFirmware;SampleFirmware" ^
    --add-data "README.md;." ^
    --add-data "DEPENDENCY_INSTALLER_README.md;." ^
    --add-data "requirements.txt;." ^
    --hidden-import serial ^
    --hidden-import serial.tools.list_ports ^
    --hidden-import esptool ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.messagebox ^
    --hidden-import threading ^
    --hidden-import subprocess ^
    --hidden-import datetime ^
    --hidden-import importlib.util ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --exclude-module PIL ^
    --exclude-module cv2 ^
    --exclude-module tensorflow ^
    --exclude-module torch ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module IPython ^
    --exclude-module pytest ^
    --exclude-module unittest ^
    --exclude-module doctest ^
    --exclude-module pdb ^
    --exclude-module profile ^
    --exclude-module cProfile ^
    --exclude-module pstats ^
    --exclude-module trace ^
    --exclude-module distutils ^
    --exclude-module setuptools ^
    --exclude-module pip ^
    --exclude-module wheel ^
    --exclude-module pkg_resources ^
    main.py

echo.
if exist "dist\J_Tech_Pixel_Uploader_v2.0_Final.exe" (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created: dist\J_Tech_Pixel_Uploader_v2.0_Final.exe
    echo.
    echo Size: 
    for %%A in ("dist\J_Tech_Pixel_Uploader_v2.0_Final.exe") do echo %%~zA bytes
    echo.
    echo Ready for distribution!
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the error messages above.
)

echo.
echo Press any key to exit...
pause >nul
