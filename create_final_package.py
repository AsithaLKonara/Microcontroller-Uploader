#!/usr/bin/env python3
"""
Final Package Creator for J Tech Pixel Uploader v2.0
This script creates a complete distribution package
"""

import os
import shutil
import zipfile
from datetime import datetime
import subprocess
import sys

def create_final_package():
    """Create the final installer package"""
    print("🚀 Creating J Tech Pixel Uploader v2.0 Final Package")
    print("=" * 60)
    
    # Create package directory
    package_name = "J_Tech_Pixel_Uploader_v2.0_Final_Package"
    package_dir = f"./{package_name}"
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    os.makedirs(package_dir)
    os.makedirs(f"{package_dir}/SampleFirmware")
    
    # Copy main executable
    exe_source = "./dist/J_Tech_Pixel_Uploader_v2.0_Final.exe"
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, package_dir)
        print(f"✅ Copied executable: {os.path.basename(exe_source)}")
    else:
        print("❌ Executable not found! Please build first.")
        return False
    
    # Copy essential files
    essential_files = [
        "README.md",
        "DEPENDENCY_INSTALLER_README.md",
        "requirements.txt",
        "config.py",
        "utils.py"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"✅ Copied: {file}")
        else:
            print(f"⚠️ Warning: {file} not found")
    
    # Copy SampleFirmware directory
    if os.path.exists("SampleFirmware"):
        for item in os.listdir("SampleFirmware"):
            source = os.path.join("SampleFirmware", item)
            dest = os.path.join(package_dir, "SampleFirmware", item)
            if os.path.isfile(source):
                shutil.copy2(source, dest)
            elif os.path.isdir(source):
                shutil.copytree(source, dest)
        print("✅ Copied SampleFirmware directory")
    
    # Create installation instructions
    create_install_instructions(package_dir)
    
    # Create version info
    create_version_info(package_dir)
    
    # Create package info
    create_package_info(package_dir)
    
    # Create ZIP package
    zip_name = f"{package_name}.zip"
    create_zip_package(package_dir, zip_name)
    
    print("\n" + "=" * 60)
    print("🎉 FINAL PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📦 Package: {package_name}")
    print(f"🗜️  ZIP Archive: {zip_name}")
    print(f"📁 Location: {os.path.abspath(package_dir)}")
    print(f"📊 Size: {get_directory_size(package_dir):.1f} MB")
    print("\n🚀 Ready for distribution!")
    
    return True

def create_install_instructions(package_dir):
    """Create installation instructions"""
    instructions = """J Tech Pixel Uploader v2.0 Final - Installation Instructions
================================================================

QUICK START:
1. Extract this ZIP file to any folder
2. Double-click "J_Tech_Pixel_Uploader_v2.0_Final.exe"
3. The software will automatically check and install dependencies
4. Connect your ESP8266/ESP32 device and start uploading!

FEATURES:
✅ Automatic dependency installation
✅ ESP8266/ESP32 support
✅ Multiple firmware formats (.bin, .hex, .dat)
✅ Professional GUI with real-time progress
✅ Comprehensive logging and error handling
✅ Sample firmware included

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- USB port for device connection
- Internet connection for dependency installation

SUPPORTED DEVICES:
- ESP8266 (NodeMCU, Wemos D1 Mini)
- ESP32 (DevKit, ESP32-WROOM)
- AVR (Arduino Uno, Nano, Pro Mini)
- STM32 (STM32F103, STM32F407)

FIRMWARE FORMATS:
- .bin - Binary files (ESP devices)
- .hex - Intel HEX files (AVR devices)
- .dat - Data files (filesystem mode)

TROUBLESHOOTING:
- If dependencies fail to install, run as Administrator
- Ensure device is in flash mode (GPIO0 for ESP devices)
- Check USB drivers are installed
- Try different USB ports

For more information, see README.md and DEPENDENCY_INSTALLER_README.md

© 2024 J Tech Pixel - Professional Microcontroller Solutions
"""
    
    with open(f"{package_dir}/INSTALL_INSTRUCTIONS.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("✅ Created installation instructions")

def create_version_info(package_dir):
    """Create version information file"""
    version_info = f"""J Tech Pixel Uploader v2.0 Final
Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python Version: {sys.version}
Platform: {sys.platform}

Features:
- Automatic dependency checker and installer
- Professional GUI with responsive design
- Multi-device support (ESP8266, ESP32, AVR, STM32)
- Real-time upload progress and logging
- Smart file validation and conversion
- Comprehensive error handling and troubleshooting

Dependencies:
- pyserial (automatic installation)
- esptool (automatic installation)
- tkinter (included with Python)

Sample Firmware:
- 8x8 LED matrix patterns
- 16x16 LED matrix patterns
- ESP8266/ESP32 examples
- Various animation patterns

This is a standalone executable - no Python installation required!
"""
    
    with open(f"{package_dir}/VERSION_INFO.txt", "w", encoding="utf-8") as f:
        f.write(version_info)
    
    print("✅ Created version information")

def create_package_info(package_dir):
    """Create package information"""
    package_info = f"""J Tech Pixel Uploader v2.0 Final Package
===============================================

Package Contents:
- J_Tech_Pixel_Uploader_v2.0_Final.exe (Main executable)
- SampleFirmware/ (Sample firmware files)
- README.md (Main documentation)
- DEPENDENCY_INSTALLER_README.md (Dependency system docs)
- requirements.txt (Python dependencies list)
- config.py (Configuration file)
- utils.py (Utility functions)
- INSTALL_INSTRUCTIONS.txt (This file)
- VERSION_INFO.txt (Version and feature info)

Package Details:
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Type: Standalone Windows Executable
- Architecture: 64-bit
- Dependencies: Auto-installing
- Size: {get_directory_size(package_dir):.1f} MB

Distribution:
This package is ready for distribution to end users.
No additional installation steps required.
"""
    
    with open(f"{package_dir}/PACKAGE_INFO.txt", "w", encoding="utf-8") as f:
        f.write(package_info)
    
    print("✅ Created package information")

def create_zip_package(package_dir, zip_name):
    """Create ZIP archive of the package"""
    print(f"🗜️ Creating ZIP archive: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created ZIP archive: {zip_name}")

def get_directory_size(directory):
    """Get directory size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Convert to MB

def main():
    """Main function"""
    print("J Tech Pixel Uploader v2.0 Final Package Creator")
    print("=" * 60)
    
    # Check if executable exists
    if not os.path.exists("./dist/J_Tech_Pixel_Uploader_v2.0_Final.exe"):
        print("❌ Executable not found!")
        print("Please run the build script first:")
        print("  - build_final_installer.bat (Windows)")
        print("  - build_final_installer.ps1 (PowerShell)")
        return
    
    # Create package
    if create_final_package():
        print("\n🎯 Package creation completed successfully!")
        print("📦 The final installer package is ready for distribution.")
    else:
        print("\n❌ Package creation failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
