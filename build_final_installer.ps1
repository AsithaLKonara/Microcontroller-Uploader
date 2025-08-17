Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building J Tech Pixel Uploader v2.0 Final" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "*.spec") { Remove-Item "*.spec" -Force }

Write-Host ""
Write-Host "Building with PyInstaller..." -ForegroundColor Yellow

try {
    pyinstaller --clean --onefile --windowed --name "J_Tech_Pixel_Uploader_v2.0_Final" `
        --add-data "config.py;." `
        --add-data "utils.py;." `
        --add-data "SampleFirmware;SampleFirmware" `
        --add-data "README.md;." `
        --add-data "DEPENDENCY_INSTALLER_README.md;." `
        --add-data "requirements.txt;." `
        --hidden-import serial `
        --hidden-import serial.tools.list_ports `
        --hidden-import esptool `
        --hidden-import tkinter `
        --hidden-import tkinter.ttk `
        --hidden-import tkinter.filedialog `
        --hidden-import tkinter.messagebox `
        --hidden-import threading `
        --hidden-import subprocess `
        --hidden-import datetime `
        --hidden-import importlib.util `
        --exclude-module matplotlib `
        --exclude-module numpy `
        --exclude-module scipy `
        --exclude-module pandas `
        --exclude-module PIL `
        --exclude-module cv2 `
        --exclude-module tensorflow `
        --exclude-module torch `
        --exclude-module jupyter `
        --exclude-module notebook `
        --exclude-module IPython `
        --exclude-module pytest `
        --exclude-module unittest `
        --exclude-module doctest `
        --exclude-module pdb `
        --exclude-module profile `
        --exclude-module cProfile `
        --exclude-module pstats `
        --exclude-module trace `
        --exclude-module distutils `
        --exclude-module setuptools `
        --exclude-module pip `
        --exclude-module wheel `
        --exclude-module pkg_resources `
        main.py

    Write-Host ""
    if (Test-Path "dist\J_Tech_Pixel_Uploader_v2.0_Final.exe") {
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Executable created: dist\J_Tech_Pixel_Uploader_v2.0_Final.exe" -ForegroundColor Green
        Write-Host ""
        
        $fileInfo = Get-Item "dist\J_Tech_Pixel_Uploader_v2.0_Final.exe"
        $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
        $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        Write-Host "Size: $($fileInfo.Length) bytes ($sizeKB KB, $sizeMB MB)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Ready for distribution!" -ForegroundColor Green
    } else {
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "BUILD FAILED!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "Check the error messages above." -ForegroundColor Red
    }
} catch {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD ERROR!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
