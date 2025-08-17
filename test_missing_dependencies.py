#!/usr/bin/env python3
"""
Test script to simulate missing dependencies and test the dependency installer
This script temporarily modifies the import behavior to test the installer
"""

import sys
import os
import importlib.util

# Store original import behavior
original_find_spec = importlib.util.find_spec

def mock_missing_package(package_name):
    """Mock function to simulate a missing package"""
    def mock_find_spec(name, package=None):
        if name == package_name:
            return None  # Package not found
        return original_find_spec(name, package)
    return mock_find_spec

def test_missing_pyserial():
    """Test the dependency installer with missing pyserial"""
    print("🧪 Testing dependency installer with missing pyserial...")
    
    # Mock missing pyserial
    importlib.util.find_spec = mock_missing_package('serial')
    
    try:
        # Try to import the main application
        from main import JTechPixelUploader
        print("✅ Main application imported successfully")
        
        # Test dependency checking methods
        app = None
        try:
            # Create a mock root window for testing
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            app = JTechPixelUploader(root)
            print("✅ Application created successfully")
            
            # Test dependency checking
            missing = app.check_and_install_dependencies()
            print(f"✅ Dependency check completed")
            
        except Exception as e:
            print(f"⚠️ Expected error during dependency check: {e}")
            
        finally:
            if app and hasattr(app, 'root'):
                app.root.destroy()
            root.destroy()
            
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
    finally:
        # Restore original import behavior
        importlib.util.find_spec = original_find_spec

def test_missing_esptool():
    """Test the dependency installer with missing esptool"""
    print("\n🧪 Testing dependency installer with missing esptool...")
    
    # Mock missing esptool
    importlib.util.find_spec = mock_missing_package('esptool')
    
    try:
        # Try to import the main application
        from main import JTechPixelUploader
        print("✅ Main application imported successfully")
        
        # Test dependency checking methods
        app = None
        try:
            # Create a mock root window for testing
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            app = JTechPixelUploader(root)
            print("✅ Application created successfully")
            
            # Test dependency checking
            missing = app.check_and_install_dependencies()
            print(f"✅ Dependency check completed")
            
        except Exception as e:
            print(f"⚠️ Expected error during dependency check: {e}")
            
        finally:
            if app and hasattr(app, 'root'):
                app.root.destroy()
            root.destroy()
            
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
    finally:
        # Restore original import behavior
        importlib.util.find_spec = original_find_spec

def main():
    """Main test function"""
    print("🧪 Testing Dependency Installer with Missing Dependencies")
    print("=" * 60)
    
    # Test with missing pyserial
    test_missing_pyserial()
    
    # Test with missing esptool
    test_missing_esptool()
    
    print("\n" + "=" * 60)
    print("✅ Dependency installer tests completed!")
    print("💡 Check the application logs for detailed information")

if __name__ == "__main__":
    main()
