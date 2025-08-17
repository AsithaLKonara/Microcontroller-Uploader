#!/usr/bin/env python3
"""
Simple test for core dependency checking logic
"""

import sys
import importlib.util
import subprocess

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

def test_dependency_logic():
    """Test the core dependency checking logic"""
    print("🧪 Testing Core Dependency Logic")
    print("=" * 40)
    
    # Test package availability
    print("\n📦 Testing package availability:")
    
    pyserial_ok = check_package_available('serial')
    print(f"pyserial: {'✅ Available' if pyserial_ok else '❌ Missing'}")
    
    esptool_ok = check_esptool_available()
    print(f"esptool:  {'✅ Available' if esptool_ok else '❌ Missing'}")
    
    # Test with non-existent package
    fake_package_ok = check_package_available('this_package_does_not_exist')
    print(f"fake package: {'✅ Available' if fake_package_ok else '❌ Missing'}")
    
    # Summary
    print("\n📋 Summary:")
    if pyserial_ok and esptool_ok:
        print("🎉 All required dependencies are available!")
        print("🚀 The software should run without issues")
    else:
        missing = []
        if not pyserial_ok:
            missing.append("pyserial")
        if not esptool_ok:
            missing.append("esptool")
        print(f"⚠️ Missing packages: {', '.join(missing)}")
        print("💡 Install with: pip install " + " ".join(missing))
    
    print("\n✅ Core dependency logic test completed!")

if __name__ == "__main__":
    test_dependency_logic()
