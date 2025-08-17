#!/usr/bin/env python3
"""
Test script for .dat file enhancements in J Tech Pixel Uploader
Tests the new features: automatic tool installation, pattern editor, and extended device support
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_automatic_tool_installation():
    """Test automatic installation of filesystem tools"""
    print("🧪 Testing Automatic Tool Installation...")
    
    try:
        # Import utils module
        import utils
        
        # Test tool detection before installation
        print("  📋 Checking initial tool availability...")
        initial_builder = utils.find_fs_builder()
        print(f"    Initial builder: {initial_builder}")
        
        # Test automatic installation
        print("  🔧 Testing automatic installation...")
        success, message = utils.download_and_install_fs_tools()
        print(f"    Installation result: {success}")
        print(f"    Message: {message}")
        
        # Test tool detection after installation
        print("  📋 Checking tool availability after installation...")
        final_builder = utils.find_fs_builder()
        print(f"    Final builder: {final_builder}")
        
        if final_builder:
            print("  ✅ Automatic tool installation working")
            return True
        else:
            print("  ❌ Automatic tool installation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing tool installation: {e}")
        return False

def test_pattern_editor_import():
    """Test that pattern editor can be imported and created"""
    print("🧪 Testing Pattern Editor Import...")
    
    try:
        # Import main module
        import main
        
        # Check if PatternEditorDialog class exists
        if hasattr(main, 'PatternEditorDialog'):
            print("  ✅ PatternEditorDialog class found")
            return True
        else:
            print("  ❌ PatternEditorDialog class not found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error importing pattern editor: {e}")
        return False

def test_extended_device_support():
    """Test extended .dat file support for more devices"""
    print("🧪 Testing Extended Device Support...")
    
    try:
        # Import config module
        import config
        
        # Check LED pattern support configuration
        if hasattr(config, 'LED_PATTERN_SUPPORT'):
            led_config = config.LED_PATTERN_SUPPORT
            print(f"  ✅ LED Pattern Support configuration found")
            print(f"    Supported devices: {len(led_config['supported_devices'])}")
            print(f"    Matrix sizes: {list(led_config['matrix_sizes'].keys())}")
            print(f"    Protocols: {led_config['protocols']}")
        else:
            print("  ❌ LED Pattern Support configuration not found")
            return False
        
        # Check device configs for .dat support
        dat_supported_devices = []
        for device, config_data in config.DEVICE_CONFIGS.items():
            if '*.dat' in config_data.get('supported_files', []):
                dat_supported_devices.append(device)
        
        print(f"  📋 Devices with .dat support: {len(dat_supported_devices)}")
        for device in dat_supported_devices:
            config_data = config.DEVICE_CONFIGS[device]
            led_support = config_data.get('led_pattern_support', False)
            matrix_sizes = config_data.get('matrix_sizes', [])
            print(f"    {device}: LED support={led_support}, Matrix sizes={matrix_sizes}")
        
        if len(dat_supported_devices) >= 10:  # Should have at least 10 devices
            print("  ✅ Extended device support working")
            return True
        else:
            print("  ❌ Insufficient device support")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing device support: {e}")
        return False

def test_filesystem_image_creation():
    """Test filesystem image creation from .dat files"""
    print("🧪 Testing Filesystem Image Creation...")
    
    try:
        import utils
        
        # Create a test .dat file
        test_dat_content = b'\x00' * 192  # 8x8 matrix (64 LEDs * 3 bytes)
        test_dat_path = "test_pattern.dat"
        
        with open(test_dat_path, 'wb') as f:
            f.write(test_dat_content)
        
        print(f"  📁 Created test .dat file: {test_dat_path}")
        
        # Test filesystem image creation
        success, output_path, error_msg = utils.create_fs_image(test_dat_path, 1)
        
        if success:
            print(f"  ✅ FS image created: {output_path}")
            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)
            return True
        else:
            print(f"  ❌ FS image creation failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing filesystem creation: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists("test_pattern.dat"):
            os.remove("test_pattern.dat")

def test_dependencies():
    """Test that new dependencies are available"""
    print("🧪 Testing New Dependencies...")
    
    try:
        # Test Pillow (PIL)
        try:
            from PIL import Image, ImageTk
            print("  ✅ Pillow (PIL) available")
            pil_ok = True
        except ImportError:
            print("  ❌ Pillow (PIL) not available")
            pil_ok = False
        
        # Test numpy
        try:
            import numpy as np
            print("  ✅ NumPy available")
            numpy_ok = True
        except ImportError:
            print("  ❌ NumPy not available")
            numpy_ok = False
        
        return pil_ok and numpy_ok
        
    except Exception as e:
        print(f"  ❌ Error testing dependencies: {e}")
        return False

def test_main_application():
    """Test that main application can start with new features"""
    print("🧪 Testing Main Application...")
    
    try:
        # Test if main module can be imported
        import main
        
        # Check if new methods exist
        if hasattr(main.JTechPixelUploader, 'open_pattern_editor'):
            print("  ✅ Pattern editor method found")
        else:
            print("  ❌ Pattern editor method not found")
            return False
        
        # Check if PatternEditorDialog is available
        if hasattr(main, 'PatternEditorDialog'):
            print("  ✅ PatternEditorDialog class available")
        else:
            print("  ❌ PatternEditorDialog class not available")
            return False
        
        print("  ✅ Main application ready with new features")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing main application: {e}")
        return False

def main():
    """Run all tests"""
    print("🎨 J Tech Pixel Uploader - .dat File Enhancements Test")
    print("=" * 60)
    
    tests = [
        ("Automatic Tool Installation", test_automatic_tool_installation),
        ("Pattern Editor Import", test_pattern_editor_import),
        ("Extended Device Support", test_extended_device_support),
        ("Filesystem Image Creation", test_filesystem_image_creation),
        ("New Dependencies", test_dependencies),
        ("Main Application", test_main_application)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! .dat file enhancements are working correctly.")
        print("\n🚀 New Features Available:")
        print("  • Automatic installation of mkspiffs/mklittlefs tools")
        print("  • Visual pattern editor for creating custom LED patterns")
        print("  • Extended .dat support for 10+ microcontroller families")
        print("  • Enhanced filesystem image creation")
        print("  • Improved device compatibility and matrix size support")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("\n💡 To fix issues:")
        print("  • Install missing dependencies: pip install Pillow numpy")
        print("  • Check that all files are properly updated")
        print("  • Verify the application can start without errors")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
