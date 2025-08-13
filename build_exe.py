#!/usr/bin/env python3
"""
Build script for J Tech Pixel Uploader executable
"""

import os
import subprocess
import shutil

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building J Tech Pixel Uploader executable...")
    
    # Create the PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI app)
        "--name=J_Tech_Pixel_Uploader", # Executable name
        "--icon=icon.ico",              # Icon (if available)
        "--add-data=config.py;.",       # Include config file
        "--add-data=utils.py;.",        # Include utils file
        "--hidden-import=serial",       # Include serial module
        "--hidden-import=serial.tools", # Include serial tools
        "--hidden-import=tkinter",      # Include tkinter
        "--hidden-import=tkinter.ttk",  # Include ttk
        "--hidden-import=tkinter.messagebox", # Include messagebox
        "--hidden-import=tkinter.filedialog", # Include filedialog
        "--hidden-import=datetime",     # Include datetime
        "--hidden-import=threading",    # Include threading
        "--hidden-import=subprocess",   # Include subprocess
        "--hidden-import=os",           # Include os
        "--hidden-import=time",         # Include time
        "--hidden-import=json",         # Include json
        "--hidden-import=math",         # Include math
        "--clean",                       # Clean build cache
        "main.py"                       # Main script
    ]
    
    # Remove icon if not available
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = "dist/J_Tech_Pixel_Uploader.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 File size: {file_size:.1f} MB")
            
            # Create a simple launcher batch file
            create_launcher()
            
            print("\n🎉 Build completed successfully!")
            print(f"💡 Your executable is ready: {exe_path}")
            print("🚀 You can now distribute this .exe file to other Windows computers!")
            
        else:
            print("❌ Executable not found in dist folder")
            print("📋 Build output:")
            print(result.stdout)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print("📋 Error output:")
        print(e.stderr)
        print("\n📋 Build output:")
        print(e.stdout)

def create_launcher():
    """Create a simple launcher batch file"""
    launcher_content = """@echo off
echo Starting J Tech Pixel Uploader...
echo.
echo If you get any errors, make sure:
echo - Your ESP device is connected
echo - You have the correct COM port
echo - The device is in flash mode
echo.
pause
start "" "J_Tech_Pixel_Uploader.exe"
"""
    
    with open("dist/Launch_Uploader.bat", "w") as f:
        f.write(launcher_content)
    
    print("📝 Created launcher: dist/Launch_Uploader.bat")

def clean_build():
    """Clean build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    dirs_to_clean = ["build", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    for pattern in files_to_clean:
        for file in os.listdir("."):
            if file.endswith(".spec"):
                os.remove(file)
                print(f"   Removed {file}")
    
    print("✅ Cleanup completed")

if __name__ == "__main__":
    print("🚀 J Tech Pixel Uploader - Build Script")
    print("=" * 50)
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    build_executable()
    
    print("\n" + "=" * 50)
    print("🏁 Build process completed!")
