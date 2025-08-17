@echo off
echo ========================================
echo J Tech Pixel Uploader v2.0 Final - Master Build
echo ========================================
echo.

echo Step 1: Building executable with PyInstaller...
echo.

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

if not exist "dist\J_Tech_Pixel_Uploader_v2.0_Final.exe" (
    echo.
    echo ❌ BUILD FAILED! Executable not created.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Executable built successfully!
echo.

echo Step 2: Creating final package...
python create_final_package.py

if exist "J_Tech_Pixel_Uploader_v2.0_Final_Package" (
    echo.
    echo ========================================
    echo 🎉 MASTER BUILD COMPLETED SUCCESSFULLY!
    echo ========================================
    echo.
    echo 📦 Final Package: J_Tech_Pixel_Uploader_v2.0_Final_Package
    echo 🗜️  ZIP Archive: J_Tech_Pixel_Uploader_v2.0_Final_Package.zip
    echo 🚀 Ready for distribution!
    echo.
    echo Location: %cd%\J_Tech_Pixel_Uploader_v2.0_Final_Package
) else (
    echo.
    echo ❌ Package creation failed!
    echo Please check the error messages above.
)

echo.
echo Press any key to exit...
pause >nul
