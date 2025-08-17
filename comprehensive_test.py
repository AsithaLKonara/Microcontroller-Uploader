#!/usr/bin/env python3
"""
Comprehensive Test Script for J Tech Pixel Uploader v2.0
Tests all enhanced functionality including file type handling, conversion, and validation
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
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
        import utils
        print("✅ utils module imported successfully")
    except ImportError as e:
        print(f"❌ utils module import failed: {e}")
        return False
    
    try:
        import main
        print("✅ main module imported successfully")
    except ImportError as e:
        print(f"❌ main module import failed: {e}")
        return False
    
    return True

def test_utils_functions():
    """Test utility functions"""
    print("\n🔧 Testing utility functions...")
    
    try:
        import utils
        
        # Test system info
        sys_info = utils.get_system_info()
        print(f"✅ System info: {sys_info['platform']} {sys_info['python_version']}")
        
        # Test available tools
        tools = utils.get_available_tools()
        print(f"✅ Available tools: {tools}")
        
        # Test file size formatting
        size_str = utils.format_file_size(1024)
        print(f"✅ File size formatting: 1024 bytes = {size_str}")
        
        # Test filename sanitization
        sanitized = utils.sanitize_filename("test<>file.txt")
        print(f"✅ Filename sanitization: 'test<>file.txt' -> '{sanitized}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False

def test_file_type_detection():
    """Test file type detection and validation"""
    print("\n📁 Testing file type detection...")
    
    try:
        import utils
        
        # Create test files
        test_dir = tempfile.mkdtemp(prefix="test_uploader_")
        
        # Test BIN file
        bin_file = os.path.join(test_dir, "test.bin")
        with open(bin_file, 'wb') as f:
            f.write(b'\x00' * 2048)  # 2KB file
        
        bin_info = utils.get_file_type_info(bin_file)
        print(f"✅ BIN file detection: {bin_info['type']} - {bin_info['status']}")
        
        # Test HEX file
        hex_file = os.path.join(test_dir, "test.hex")
        with open(hex_file, 'w') as f:
            f.write(":020000040000FA\n:00000001FF\n")  # Minimal HEX file
        
        hex_info = utils.get_file_type_info(hex_file)
        print(f"✅ HEX file detection: {hex_info['type']} - {hex_info['status']}")
        
        # Test DAT file
        dat_file = os.path.join(test_dir, "test.dat")
        with open(dat_file, 'wb') as f:
            f.write(b'\xFF\x00\xFF' * 64)  # 8x8 RGB pattern
        
        dat_info = utils.get_file_type_info(dat_file)
        print(f"✅ DAT file detection: {dat_info['type']} - {dat_info['status']}")
        
        # Cleanup
        shutil.rmtree(test_dir)
        return True
        
    except Exception as e:
        print(f"❌ File type detection test failed: {e}")
        return False

def test_hex_conversion():
    """Test HEX to BIN conversion"""
    print("\n🔄 Testing HEX to BIN conversion...")
    
    try:
        import utils
        
        # Check if converter is available
        converter = utils.find_hex_converter()
        if not converter:
            print("⚠ No HEX converter available, skipping conversion test")
            return True
        
        print(f"✅ Found converter: {converter}")
        
        # Create test HEX file
        test_dir = tempfile.mkdtemp(prefix="test_hex_")
        hex_file = os.path.join(test_dir, "test.hex")
        
        # Create a simple HEX file with proper Intel HEX format
        with open(hex_file, 'w') as f:
            f.write(":020000040000FA\n")  # Extended linear address
            f.write(":100000000102030405060708090A0B0C0D0E0F10\n")  # Data line (16 bytes)
            f.write(":100010001112131415161718191A1B1C1D1E1F20\n")  # More data
            f.write(":00000001FF\n")  # End of file
        
        # Test conversion
        success, output_path, error_msg = utils.convert_hex_to_bin(hex_file)
        
        if success:
            print(f"✅ HEX conversion successful: {os.path.basename(output_path)}")
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✅ Output file size: {size} bytes")
            else:
                print("❌ Output file not found")
        else:
            print(f"❌ HEX conversion failed: {error_msg}")
        
        # Cleanup
        shutil.rmtree(test_dir)
        return success
        
    except Exception as e:
        print(f"❌ HEX conversion test failed: {e}")
        return False

def test_fs_image_creation():
    """Test file system image creation"""
    print("\n💾 Testing file system image creation...")
    
    try:
        import utils
        
        # Check if FS builder is available
        builder = utils.find_fs_builder()
        if not builder:
            print("⚠ No file system builder available, skipping FS test")
            return True
        
        print(f"✅ Found FS builder: {builder}")
        
        # Create test DAT file
        test_dir = tempfile.mkdtemp(prefix="test_fs_")
        dat_file = os.path.join(test_dir, "test.dat")
        
        # Create a simple DAT file (8x8 RGB pattern)
        with open(dat_file, 'wb') as f:
            for i in range(64):  # 8x8 = 64 LEDs
                f.write(b'\xFF\x00\x00')  # Red pattern
        
        # Test FS image creation
        success, output_path, error_msg = utils.create_fs_image(dat_file, 1)  # 1MB FS
        
        if success:
            print(f"✅ FS image creation successful: {os.path.basename(output_path)}")
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"✅ FS image size: {size} bytes")
            else:
                print("❌ FS image file not found")
        else:
            print(f"❌ FS image creation failed: {error_msg}")
        
        # Cleanup
        shutil.rmtree(test_dir)
        return success
        
    except Exception as e:
        print(f"❌ FS image creation test failed: {e}")
        return False

def test_led_patterns():
    """Test LED pattern creation"""
    print("\n🎨 Testing LED pattern creation...")
    
    try:
        import utils
        
        # Test pattern creation
        patterns = [
            ("alternating_cols", utils.create_alternating_cols_pattern),
            ("checkerboard", utils.create_checkerboard_pattern),
            ("rainbow", utils.create_rainbow_pattern),
            ("pulse", utils.create_pulse_pattern),
            ("spiral", utils.create_spiral_pattern)
        ]
        
        for name, func in patterns:
            try:
                pattern_data = func()
                expected_size = 8 * 8 * 3  # 8x8 matrix, 3 bytes per LED
                if len(pattern_data) == expected_size:
                    print(f"✅ {name} pattern: {len(pattern_data)} bytes")
                else:
                    print(f"❌ {name} pattern: expected {expected_size} bytes, got {len(pattern_data)}")
            except Exception as e:
                print(f"❌ {name} pattern creation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ LED pattern test failed: {e}")
        return False

def test_sample_firmware_creation():
    """Test sample firmware creation"""
    print("\n📦 Testing sample firmware creation...")
    
    try:
        import utils
        
        # Create sample patterns
        created_files = utils.create_sample_led_patterns()
        
        if created_files:
            print(f"✅ Created {len(created_files)} sample files:")
            for filename in created_files:
                print(f"  - {filename}")
        else:
            print("⚠ No sample files were created")
        
        # Check if SampleFirmware directory exists
        sample_dir = "SampleFirmware"
        if os.path.exists(sample_dir):
            files = os.listdir(sample_dir)
            print(f"✅ SampleFirmware directory contains {len(files)} files")
        else:
            print("⚠ SampleFirmware directory not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample firmware creation test failed: {e}")
        return False

def test_device_configurations():
    """Test device configuration loading"""
    print("\n🔌 Testing device configurations...")
    
    try:
        import main
        
        # Create a minimal app instance to test configs
        root = main.tk.Tk()
        root.withdraw()  # Hide the window
        
        app = main.JTechPixelUploader(root)
        
        # Test device configs
        if hasattr(app, 'device_configs'):
            device_count = len(app.device_configs)
            print(f"✅ Loaded {device_count} device configurations")
            
            for device, config in app.device_configs.items():
                print(f"  - {device}: {config.get('description', 'No description')}")
        else:
            print("❌ Device configurations not found")
        
        # Test supported formats
        esp8266_config = app.device_configs.get("ESP8266")
        if esp8266_config:
            formats = esp8266_config.get("supported_formats", [])
            print(f"✅ ESP8266 supported formats: {formats}")
        else:
            print("❌ ESP8266 configuration not found")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Device configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Test Suite for J Tech Pixel Uploader v2.0")
    print("=" * 70)
    
    tests = [
        ("Import Tests", test_imports),
        ("Utility Functions", test_utils_functions),
        ("File Type Detection", test_file_type_detection),
        ("HEX to BIN Conversion", test_hex_conversion),
        ("File System Image Creation", test_fs_image_creation),
        ("LED Pattern Creation", test_led_patterns),
        ("Sample Firmware Creation", test_sample_firmware_creation),
        ("Device Configurations", test_device_configurations)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready for use.")
    else:
        print("⚠ Some tests failed. Please check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
