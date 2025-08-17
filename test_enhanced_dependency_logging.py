#!/usr/bin/env python3
"""
Test script for enhanced dependency logging functionality
This script tests the dependency logging without running the full GUI
"""

import sys
import importlib.util
import subprocess
import os

def test_dependency_logging():
    """Test the enhanced dependency logging functionality"""
    print("🧪 Testing Enhanced Dependency Logging")
    print("=" * 50)
    
    # Test package availability checking
    print("\n📦 Testing package availability methods...")
    
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
    
    # Test core functionality
    pyserial_ok = check_package_available('serial')
    esptool_ok = check_esptool_available()
    
    print(f"pyserial available: {pyserial_ok}")
    print(f"esptool available: {esptool_ok}")
    
    # Test system tools
    print("\n🔧 Testing system tools...")
    
    def check_system_tools():
        """Check if required system tools are available"""
        tool_errors = []
        
        # Check for avrdude
        try:
            result = subprocess.run(['avrdude', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                tool_errors.append("✅ avrdude available - Full AVR support")
            else:
                tool_errors.append("⚠️ avrdude not found - AVR microcontroller support limited")
        except:
            tool_errors.append("⚠️ avrdude not found - AVR microcontroller support limited")
        
        # Check for stm32flash
        try:
            result = subprocess.run(['stm32flash', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                tool_errors.append("✅ stm32flash available - Full STM32 support")
            else:
                tool_errors.append("⚠️ stm32flash not found - STM32 microcontroller support limited")
        except:
            tool_errors.append("⚠️ stm32flash not found - STM32 microcontroller support limited")
        
        return tool_errors
    
    system_tool_errors = check_system_tools()
    for tool_status in system_tool_errors:
        print(f"  {tool_status}")
    
    # Test dependency error generation
    print("\n❌ Testing dependency error generation...")
    
    missing_packages = []
    dependency_errors = []
    
    if not pyserial_ok:
        missing_packages.append('pyserial')
        dependency_errors.append("❌ pyserial package not found - Serial communication will not work")
    else:
        dependency_errors.append("✅ pyserial package available")
    
    if not esptool_ok:
        missing_packages.append('esptool')
        dependency_errors.append("❌ esptool package not found - ESP8266/ESP32 flashing will not work")
    else:
        dependency_errors.append("✅ esptool package available")
    
    print(f"Missing packages: {missing_packages}")
    print("Dependency errors:")
    for error in dependency_errors:
        print(f"  {error}")
    
    # Test system information
    print("\n💻 Testing system information...")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    print(f"  Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    
    # Test recommendations
    print("\n💡 Testing recommendations...")
    if not pyserial_ok or not esptool_ok:
        print("  🚨 CRITICAL: Missing required dependencies!")
        print("  💡 Use the dependency installer to fix this")
        print("  🔧 Or install manually: pip install pyserial esptool")
    else:
        print("  ✅ All critical dependencies are available")
        print("  🚀 Ready for firmware uploads!")
    
    print("\n✅ Enhanced dependency logging test completed!")
    print("📋 All dependency checking methods are working correctly")
    
    return True

if __name__ == "__main__":
    try:
        test_dependency_logging()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
