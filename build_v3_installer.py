#!/usr/bin/env python3
"""
Build Script for J Tech Pixel Uploader v3.0
Creates the final executable installer package
"""

import os
import sys
import shutil
import subprocess
import zipfile
from datetime import datetime

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔨 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def create_version_info():
    """Create version info file"""
    version_info = f"""J Tech Pixel Uploader v3.0
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Features:
✅ 25 ICs Support (ESP, AVR, STM32, RP2040, Teensy, Arduino, etc.)
✅ Enhanced .dat File Support with Visual Pattern Editor
✅ Automatic Dependency Installation
✅ Advanced Firmware Validation
✅ Hardware Reset Features
✅ Professional UI with Responsive Design
✅ Comprehensive Error Logging
✅ Multi-format Firmware Support (.bin, .hex, .dat, .uf2, .elf)
✅ LED Pattern Protocol (LEDP) Support
✅ Filesystem Image Creation (SPIFFS/LittleFS)
✅ Cross-platform Compatibility

Dependencies:
- Python 3.7+
- pyserial, esptool, Pillow, numpy
- System tools: avrdude, stm32flash, rp2040, etc.

This is the final v3.0 release with all enhanced features implemented.
"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("📝 Version info file created")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🚀 Building J Tech Pixel Uploader v3.0...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Build using spec file
    if not run_command('pyinstaller J_Tech_Pixel_Uploader_v3.0.spec', "Building executable"):
        return False
    
    print("✅ Executable built successfully")
    return True

def create_installer_package():
    """Create the final installer package"""
    print("📦 Creating installer package...")
    
    # Create installer directory
    installer_dir = "J_Tech_Pixel_Uploader_v3.0_Installer"
    if os.path.exists(installer_dir):
        shutil.rmtree(installer_dir)
    
    os.makedirs(installer_dir)
    
    # Copy executable
    exe_path = os.path.join("dist", "J_Tech_Pixel_Uploader_v3.0.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, installer_dir)
        print("✅ Executable copied")
    else:
        print("❌ Executable not found")
        return False
    
    # Copy documentation
    docs = [
        'README.md',
        'README_ENHANCED.md',
        '25_ICS_SUPPORT_COMPLETE.md',
        'DAT_FILE_ENHANCEMENTS.md',
        'ENHANCED_FEATURES_SUMMARY.md',
        'UI_IMPROVEMENTS_IMPLEMENTED.md',
        'VALIDATION_SYSTEM_SUMMARY.md',
        'FIRMWARE_VALIDATION_README.md',
        'ENHANCED_RESET_FEATURES.md',
        'ENHANCED_UPLOADER_IMPROVEMENTS.md',
        'PROJECT_STRUCTURE.md',
        'COMPLETE_FUNCTIONAL_OVERVIEW.md',
        'UI_LAYOUT_DESCRIPTION.md',
        'UI_UX_IMPROVEMENTS_SUMMARY.md',
        'PIXEL_FIX_CHECKLIST.txt',
        'GIT_COMMANDS.txt',
        'version_info.txt'
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, installer_dir)
    
    print("✅ Documentation copied")
    
    # Copy sample firmware
    if os.path.exists('SampleFirmware'):
        shutil.copytree('SampleFirmware', os.path.join(installer_dir, 'SampleFirmware'))
        print("✅ Sample firmware copied")
    
    # Copy requirements
    if os.path.exists('requirements.txt'):
        shutil.copy2('requirements.txt', installer_dir)
        print("✅ Requirements file copied")
    
    # Create install instructions
    install_instructions = """J Tech Pixel Uploader v3.0 - Installation Instructions

🚀 INSTALLATION:
1. Extract this package to your desired location
2. Run J_Tech_Pixel_Uploader_v3.0.exe
3. The application will automatically check and install dependencies
4. No additional setup required!

✨ FEATURES:
- 25 ICs Support (ESP, AVR, STM32, RP2040, Teensy, Arduino, etc.)
- Enhanced .dat File Support with Visual Pattern Editor
- Automatic Dependency Installation
- Advanced Firmware Validation
- Hardware Reset Features
- Professional UI with Responsive Design
- Comprehensive Error Logging
- Multi-format Firmware Support (.bin, .hex, .dat, .uf2, .elf)
- LED Pattern Protocol (LEDP) Support
- Filesystem Image Creation (SPIFFS/LittleFS)

📚 DOCUMENTATION:
- README.md - Basic usage
- README_ENHANCED.md - Enhanced features
- 25_ICS_SUPPORT.md - Complete IC support list
- DAT_FILE_SUPPORT_ENHANCEMENTS.md - .dat file features
- ENHANCED_FEATURES_SUMMARY.md - Feature overview
- UI_IMPROVEMENTS_IMPLEMENTED.md - UI enhancements
- VALIDATION_SYSTEM_SUMMARY.md - Firmware validation
- FIRMWARE_VALIDATION_README.md - Validation details
- ENHANCED_RESET_FEATURES.md - Hardware reset features
- ENHANCED_UPLOADER_IMPROVEMENTS.md - Uploader improvements
- PROJECT_STRUCTURE.md - Project organization
- COMPLETE_FUNCTIONAL_OVERVIEW.md - Complete functionality
- UI_LAYOUT_DESCRIPTION.md - UI layout details
- UI_UX_IMPROVEMENTS_SUMMARY.md - UX improvements
- PIXEL_FIX_CHECKLIST.txt - Pixel troubleshooting
- GIT_COMMANDS.txt - Git operations

🔧 SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- Python 3.7+ (automatically managed)
- Internet connection for dependency installation

💡 TROUBLESHOOTING:
- If you encounter issues, check the application log
- Dependencies are automatically installed on first run
- Sample firmware included for testing

🎉 ENJOY YOUR ENHANCED UPLOADER!
"""
    
    with open(os.path.join(installer_dir, 'INSTALL_INSTRUCTIONS.txt'), 'w', encoding='utf-8') as f:
        f.write(install_instructions)
    
    print("✅ Install instructions created")
    
    return installer_dir

def create_zip_package(installer_dir):
    """Create ZIP package"""
    print("📦 Creating ZIP package...")
    
    zip_name = f"{installer_dir}.zip"
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(installer_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, installer_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ ZIP package created: {zip_name}")
    return zip_name

def main():
    """Main build process"""
    print("🏗️  J Tech Pixel Uploader v3.0 - Build Process")
    print("=" * 50)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} available")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        if not run_command('pip install pyinstaller', "Installing PyInstaller"):
            print("❌ Failed to install PyInstaller")
            return False
    
    # Create version info
    create_version_info()
    
    # Build executable
    if not build_executable():
        print("❌ Build failed")
        return False
    
    # Create installer package
    installer_dir = create_installer_package()
    if not installer_dir:
        print("❌ Installer package creation failed")
        return False
    
    # Create ZIP package
    zip_name = create_zip_package(installer_dir)
    
    print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"📁 Installer Directory: {installer_dir}")
    print(f"📦 ZIP Package: {zip_name}")
    print(f"📱 Executable: {installer_dir}/J_Tech_Pixel_Uploader_v3.0.exe")
    print("\n✨ Your v3.0 installer is ready!")
    print("💡 Users can extract and run the executable directly")
    print("🚀 All dependencies will be automatically managed")

if __name__ == "__main__":
    main()
