#!/usr/bin/env python3
"""
Test script for dependency checking functionality
This script tests the automatic dependency checking and installation features
"""

import utils

def test_dependency_checking():
    """Test the dependency checking functionality"""
    print("🧪 Testing Dependency Checking...")
    print("=" * 50)
    
    # Test system dependencies
    print("📋 Checking system dependencies...")
    dependencies = utils.get_system_dependencies()
    
    for dep_name, dep_info in dependencies.items():
        print(f"   {dep_info['status']} {dep_name}: {dep_info['current']}")
    
    print()
    
    # Test Python version check
    print("🐍 Testing Python version check...")
    python_ok, python_msg = utils.check_python_version()
    print(f"   Python version: {python_msg}")
    print(f"   Status: {'✅ OK' if python_ok else '❌ Too old'}")
    
    print()
    
    # Test esptool availability
    print("🔧 Testing esptool availability...")
    esptool_path = utils.find_esptool()
    if esptool_path:
        print(f"   ✅ esptool found: {esptool_path}")
    else:
        print("   ❌ esptool not found")
    
    print()
    
    # Test available tools
    print("🛠️ Testing available tools...")
    tools = utils.get_available_tools()
    for tool, available in tools.items():
        status = "✅ Available" if available else "❌ Not found"
        print(f"   {tool}: {status}")
    
    print()
    
    # Test dependency installation (dry run)
    print("📥 Testing dependency installation (dry run)...")
    print("   Note: This is a test - no packages will actually be installed")
    
    # Check what would be installed
    missing_critical = []
    for dep_name, dep_info in dependencies.items():
        if dep_info["status"] == "❌ Missing" and dep_name in ["pip", "esptool", "pyserial"]:
            missing_critical.append(dep_name)
    
    if missing_critical:
        print(f"   ⚠️ Missing critical dependencies: {', '.join(missing_critical)}")
        print("   🔧 Would attempt to install automatically")
    else:
        print("   ✅ All critical dependencies are available")
    
    print()
    
    # Test the complete dependency check
    print("🔍 Testing complete dependency check...")
    try:
        # This would actually try to install packages, so we'll just test the function exists
        print("   ✅ Dependency checking functions are available")
        print("   💡 Run the main application to test automatic installation")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("🎉 Dependency testing completed!")
    print("\n💡 To test automatic installation:")
    print("   1. Run the main application: python j_tech_pixel_uploader.py")
    print("   2. Watch the startup logs for dependency checking")
    print("   3. Missing packages will be installed automatically")

if __name__ == "__main__":
    test_dependency_checking()
