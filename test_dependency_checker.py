#!/usr/bin/env python3
"""
Test script for dependency checking functionality
This script tests the dependency checker without running the full GUI
"""

import sys
import importlib.util
import subprocess
import os

def check_package_available(package_name):
    """Check if a Python package is available"""
    try:
        importlib.util.find_spec(package_name)
        return True
    except ImportError:
        return False

def check_esptool_available():
    """Check if esptool is available"""
    try:
        # Try to import esptool
        importlib.util.find_spec('esptool')
        return True
    except ImportError:
        # Try to run esptool command
        try:
            result = subprocess.run(['python', '-m', 'esptool', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

def check_system_tools():
    """Check if required system tools are available"""
    missing_tools = []
    
    # Check for esptool
    if not check_esptool_available():
        missing_tools.append("esptool")
    
    # Check for avrdude (if AVR support is needed)
    try:
        result = subprocess.run(['avrdude', '--help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            missing_tools.append("avrdude")
    except:
        missing_tools.append("avrdude")
    
    # Check for stm32flash (if STM32 support is needed)
    try:
        result = subprocess.run(['stm32flash', '--help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            missing_tools.append("stm32flash")
    except:
        missing_tools.append("stm32flash")
    
    return missing_tools

def main():
    """Main test function"""
    print("🔍 Testing Dependency Checker...")
    print("=" * 50)
    
    # Check Python packages
    print("\n📦 Python Package Status:")
    print("-" * 30)
    
    pyserial_ok = check_package_available('serial')
    esptool_ok = check_esptool_available()
    
    print(f"pyserial: {'✅ Available' if pyserial_ok else '❌ Missing'}")
    print(f"esptool:  {'✅ Available' if esptool_ok else '❌ Missing'}")
    
    if pyserial_ok and esptool_ok:
        print("✅ All required Python packages are available")
    else:
        missing = []
        if not pyserial_ok:
            missing.append("pyserial")
        if not esptool_ok:
            missing.append("esptool")
        print(f"⚠️ Missing packages: {', '.join(missing)}")
        print("💡 Install with: pip install " + " ".join(missing))
    
    # Check system tools
    print("\n🔧 System Tools Status:")
    print("-" * 30)
    
    system_tools = check_system_tools()
    if not system_tools:
        print("✅ All system tools are available")
    else:
        print(f"⚠️ Missing system tools: {', '.join(system_tools)}")
        print("💡 These are optional but provide enhanced microcontroller support")
    
    # Summary
    print("\n📋 Summary:")
    print("-" * 30)
    if pyserial_ok and esptool_ok:
        print("🎉 All required dependencies are available!")
        print("🚀 The software should run without issues")
    else:
        print("⚠️ Some required dependencies are missing")
        print("💡 Use the dependency installer in the main application")
        print("   or install manually with pip")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
