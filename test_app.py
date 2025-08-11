#!/usr/bin/env python3
"""
Test script for J Tech Pixel Uploader
This script tests the basic functionality without requiring hardware.
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter
        print("✅ tkinter imported successfully")
    except ImportError as e:
        print(f"❌ tkinter import failed: {e}")
        return False
    
    try:
        import serial
        print("✅ pyserial imported successfully")
    except ImportError as e:
        print(f"❌ pyserial import failed: {e}")
        return False
    
    try:
        import config
        print("✅ config module imported successfully")
    except ImportError as e:
        print(f"❌ config module import failed: {e}")
        return False
    
    try:
        import utils
        print("✅ utils module imported successfully")
    except ImportError as e:
        print(f"❌ utils module import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration functionality"""
    print("\nTesting configuration...")
    
    try:
        import config
        
        # Test device configs
        if config.DEVICE_CONFIGS:
            print(f"✅ Device configurations loaded: {len(config.DEVICE_CONFIGS)} devices")
        else:
            print("❌ No device configurations found")
            return False
        
        # Test baud rates
        if config.BAUD_RATES:
            print(f"✅ Baud rates loaded: {len(config.BAUD_RATES)} rates")
        else:
            print("❌ No baud rates found")
            return False
        
        # Test config file functions
        config_dir = config.get_config_dir()
        print(f"✅ Config directory: {config_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\nTesting utilities...")
    
    try:
        import utils
        
        # Test system info
        sys_info = utils.get_system_info()
        print(f"✅ System info: {sys_info['platform']} {sys_info['python_version']}")
        
        # Test available tools
        tools = utils.get_available_tools()
        print(f"✅ Available tools: {tools}")
        
        # Test file validation
        test_file = "test_firmware.bin"
        is_valid, msg = utils.validate_firmware_file(test_file, "ESP8266")
        print(f"✅ File validation test: {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False

def test_gui_creation():
    """Test if the GUI can be created (without showing it)"""
    print("\nTesting GUI creation...")
    
    try:
        import tkinter as tk
        from j_tech_pixel_uploader import JTechPixelUploader
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Try to create the application
        app = JTechPixelUploader(root)
        print("✅ GUI created successfully")
        
        # Clean up
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("J Tech Pixel Uploader - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Utilities", test_utils),
        ("GUI Creation", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
