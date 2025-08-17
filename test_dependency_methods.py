#!/usr/bin/env python3
"""
Simple test script for dependency checking methods
This script tests the dependency methods without creating the full UI
"""

import sys
import importlib.util

def test_dependency_methods():
    """Test the dependency checking methods directly"""
    print("🧪 Testing Dependency Methods Directly")
    print("=" * 50)
    
    try:
        # Import the main class
        from main import JTechPixelUploader
        print("✅ Main class imported successfully")
        
        # Create a mock object to test methods
        class MockRoot:
            def __init__(self):
                self.title = lambda x: None
                self.geometry = lambda x: None
                self.minsize = lambda x, y: None
                self.configure = lambda **kwargs: None
                self.bind = lambda event, func: None
                self.after = lambda ms, func: None
                self.winfo_rootx = lambda: 0
                self.winfo_rooty = lambda: 0
                self.winfo_width = lambda: 1000
                self.winfo_height = lambda: 800
                self.destroy = lambda: None
                # Mock tkinter variables
                self.tk = type('MockTk', (), {})()
                self.tk.call = lambda *args: None
        
        # Create mock root
        mock_root = MockRoot()
        
        # Test dependency checking methods
        print("\n📦 Testing package availability methods...")
        
        # Create an instance to test methods
        app = JTechPixelUploader(mock_root)
        
        # Test check_package_available
        result = app.check_package_available('serial')
        print(f"check_package_available('serial'): {result}")
        
        result = app.check_package_available('nonexistent_package')
        print(f"check_package_available('nonexistent_package'): {result}")
        
        # Test check_esptool_available
        result = app.check_esptool_available()
        print(f"check_esptool_available(): {result}")
        
        # Test the main dependency check
        print("\n🔍 Testing main dependency check...")
        app.check_and_install_dependencies()
        
        # Test dependency status display
        print("\n📊 Testing dependency status display...")
        app.show_dependency_status()
        
        # Clean up
        try:
            app.root.destroy()
        except:
            pass
        
        print("\n✅ All dependency methods tested successfully!")
        
    except Exception as e:
        print(f"❌ Error testing dependency methods: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dependency_methods()
