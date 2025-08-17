# J Tech Pixel Uploader v2.0 - Installer Build Script
# PowerShell Version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "J Tech Pixel Uploader v2.0 - Installer Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
try {
    $pyinstallerVersion = pyinstaller --version
    Write-Host "✓ PyInstaller found: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PyInstaller not found. Installing..." -ForegroundColor Red
    pip install pyinstaller
}

Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow

# Clean previous builds
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "__pycache__") { Remove-Item "__pycache__" -Recurse -Force }
if (Test-Path "*.spec") { Remove-Item "*.spec" -Force }

Write-Host "✓ Cleanup completed" -ForegroundColor Green
Write-Host ""

Write-Host "Building installer with PyInstaller..." -ForegroundColor Yellow

# Build the installer
try {
    pyinstaller --clean --onefile --windowed `
        --name "J_Tech_Pixel_Uploader_v2.0" `
        --add-data "config.py;." `
        --add-data "utils.py;." `
        --add-data "requirements.txt;." `
        --add-data "README.md;." `
        --add-data "SampleFirmware;SampleFirmware" `
        main.py

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Build completed successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Get file size
        $installerPath = "dist\J_Tech_Pixel_Uploader_v2.0.exe"
        if (Test-Path $installerPath) {
            $fileSize = (Get-Item $installerPath).Length
            $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
            Write-Host "Installer location: $installerPath" -ForegroundColor Cyan
            Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
            Write-Host ""
            
            Write-Host "Opening dist folder..." -ForegroundColor Yellow
            Start-Process "explorer.exe" -ArgumentList "dist"
        }
    } else {
        Write-Host "❌ Build failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Build error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Build process finished!" -ForegroundColor Cyan
Read-Host "Press Enter to continue"
