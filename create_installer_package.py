#!/usr/bin/env python3
"""
J Tech Pixel Uploader v2.0 - Installer Package Creator
This script creates a comprehensive installer package with PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print the header information"""
    print("=" * 60)
    print("J Tech Pixel Uploader v2.0 - Installer Package Creator")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller installed")
    
    print()

def clean_previous_builds():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}")
    
    for pattern in files_to_clean:
        for file_path in Path(".").glob(pattern):
            file_path.unlink()
            print(f"✓ Removed {file_path}")
    
    print()

def create_version_file():
    """Create a version info file for the executable"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'J Tech Pixel'),
        StringStruct(u'FileDescription', u'J Tech Pixel Uploader v2.0 - ESP8266/ESP32 LED Matrix Flasher'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'J_Tech_Pixel_Uploader'),
        StringStruct(u'LegalCopyright', u'© 2024 J Tech Pixel. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'J_Tech_Pixel_Uploader_v2.0.exe'),
        StringStruct(u'ProductName', u'J Tech Pixel Uploader'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open("version_info.txt", "w") as f:
        f.write(version_info)
    
    print("✓ Version info file created")

def build_installer():
    """Build the installer using PyInstaller"""
    print("Building installer with PyInstaller...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "J_Tech_Pixel_Uploader_v2.0",
        "--version-file", "version_info.txt",
        "--add-data", "config.py;.",
        "--add-data", "utils.py;.",
        "--add-data", "requirements.txt;.",
        "--add-data", "README.md;.",
        "--add-data", "SampleFirmware;SampleFirmware",
        "--hidden-import", "serial",
        "--hidden-import", "serial.tools.list_ports",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "threading",
        "--hidden-import", "subprocess",
        "--hidden-import", "datetime",
        "--hidden-import", "config",
        "--hidden-import", "utils",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer_package():
    """Create a complete installer package"""
    print("Creating installer package...")
    
    # Create package directory
    package_dir = "J_Tech_Pixel_Uploader_v2.0_Installer"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    os.makedirs(package_dir)
    
    # Copy executable
    exe_source = "dist/J_Tech_Pixel_Uploader_v2.0.exe"
    exe_dest = f"{package_dir}/J_Tech_Pixel_Uploader_v2.0.exe"
    
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, exe_dest)
        print(f"✓ Copied executable to {package_dir}")
    
    # Copy additional files
    additional_files = [
        "README.md",
        "requirements.txt",
        "SampleFirmware"
    ]
    
    for file_name in additional_files:
        if os.path.exists(file_name):
            if os.path.isdir(file_name):
                shutil.copytree(file_name, f"{package_dir}/{file_name}")
            else:
                shutil.copy2(file_name, f"{package_dir}/{file_name}")
            print(f"✓ Copied {file_name} to {package_dir}")
    
    # Create install instructions
    install_instructions = """J Tech Pixel Uploader v2.0 - Installation Instructions

1. Extract all files from this package to a folder of your choice
2. Run J_Tech_Pixel_Uploader_v2.0.exe to start the application
3. No additional installation is required - this is a portable application

System Requirements:
- Windows 10/11 (64-bit)
- USB ports for device connection
- Python 3.7+ (if running from source)

Features:
- ESP8266/ESP32 firmware flashing
- Support for .bin, .hex, and .dat files
- Automatic COM port detection
- Real-time upload progress
- Comprehensive logging system
- Professional light theme UI

For support or questions, please refer to the README.md file.

© 2024 J Tech Pixel. All rights reserved.
"""
    
    with open(f"{package_dir}/INSTALL_INSTRUCTIONS.txt", "w") as f:
        f.write(install_instructions)
    
    print(f"✓ Created installer package: {package_dir}")
    return package_dir

def main():
    """Main function"""
    print_header()
    
    # Check dependencies
    check_dependencies()
    
    # Clean previous builds
    clean_previous_builds()
    
    # Create version info
    create_version_file()
    
    # Build installer
    if build_installer():
        # Create package
        package_dir = create_installer_package()
        
        print()
        print("=" * 60)
        print("🎉 INSTALLER PACKAGE CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Package location: {package_dir}")
        print(f"Executable: {package_dir}/J_Tech_Pixel_Uploader_v2.0.exe")
        
        # Get file sizes
        if os.path.exists(f"{package_dir}/J_Tech_Pixel_Uploader_v2.0.exe"):
            exe_size = os.path.getsize(f"{package_dir}/J_Tech_Pixel_Uploader_v2.0.exe")
            exe_size_mb = exe_size / (1024 * 1024)
            print(f"Executable size: {exe_size_mb:.2f} MB")
        
        print()
        print("The installer package is ready for distribution!")
        print("Users can extract and run the executable directly.")
        
        # Clean up temporary files
        if os.path.exists("version_info.txt"):
            os.remove("version_info.txt")
            print("✓ Cleaned up temporary files")
        
    else:
        print("❌ Failed to create installer package")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
