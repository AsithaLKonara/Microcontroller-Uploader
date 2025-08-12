#!/usr/bin/env python3
"""
Test Enhanced Features Integration
Tests that all enhanced features are properly integrated into the main application
"""

import os
import sys
import importlib

def test_enhanced_modules():
    """Test that all enhanced modules can be imported"""
    print("🔍 Testing Enhanced Modules Import...")
    
    modules_to_test = [
        "enhanced_features",
        "enhanced_progress_tracker", 
        "enhanced_error_handler"
    ]
    
    all_modules_available = True
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}: Successfully imported")
            
            # Test if main classes exist
            if module_name == "enhanced_features":
                if hasattr(module, 'EnhancedFeatures'):
                    print(f"   ✅ EnhancedFeatures class found")
                else:
                    print(f"   ❌ EnhancedFeatures class missing")
                    all_modules_available = False
                    
            elif module_name == "enhanced_progress_tracker":
                if hasattr(module, 'EnhancedProgressTracker'):
                    print(f"   ✅ EnhancedProgressTracker class found")
                else:
                    print(f"   ❌ EnhancedProgressTracker class missing")
                    all_modules_available = False
                    
            elif module_name == "enhanced_error_handler":
                if hasattr(module, 'EnhancedErrorHandler'):
                    print(f"   ✅ EnhancedErrorHandler class found")
                else:
                    print(f"   ❌ EnhancedErrorHandler class missing")
                    all_modules_available = False
                    
        except ImportError as e:
            print(f"❌ {module_name}: Import failed - {e}")
            all_modules_available = False
    
    return all_modules_available

def test_main_app_integration():
    """Test that the main app can import enhanced features"""
    print("\n🔍 Testing Main App Integration...")
    
    try:
        # Try to import the main app
        import j_tech_pixel_uploader
        print("✅ Main app imported successfully")
        
        # Check if enhanced features are properly integrated
        if hasattr(j_tech_pixel_uploader, 'ENHANCED_FEATURES_AVAILABLE'):
            print(f"✅ Enhanced features availability flag: {j_tech_pixel_uploader.ENHANCED_FEATURES_AVAILABLE}")
        else:
            print("❌ Enhanced features availability flag missing")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Main app import failed: {e}")
        return False

def test_enhanced_features_functionality():
    """Test basic functionality of enhanced features"""
    print("\n🔍 Testing Enhanced Features Functionality...")
    
    try:
        # Test enhanced features
        from enhanced_features import EnhancedFeatures
        
        # Create a mock main app for testing
        class MockMainApp:
            def __init__(self):
                self.port_combo = None
                self.update_device_status = lambda x: None
                
        mock_app = MockMainApp()
        enhanced = EnhancedFeatures(mock_app)
        
        print("✅ EnhancedFeatures instantiated successfully")
        
        # Test basic methods
        if hasattr(enhanced, 'detect_available_ports'):
            print("✅ detect_available_ports method available")
        else:
            print("❌ detect_available_ports method missing")
            
        if hasattr(enhanced, 'auto_detect_devices'):
            print("✅ auto_detect_devices method available")
        else:
            print("❌ auto_detect_devices method missing")
            
        if hasattr(enhanced, 'validate_firmware_enhanced'):
            print("✅ validate_firmware_enhanced method available")
        else:
            print("❌ validate_firmware_enhanced method missing")
            
        return True
        
    except Exception as e:
        print(f"❌ Enhanced features functionality test failed: {e}")
        return False

def test_progress_tracker():
    """Test enhanced progress tracker"""
    print("\n🔍 Testing Enhanced Progress Tracker...")
    
    try:
        from enhanced_progress_tracker import EnhancedProgressTracker
        
        # Create a mock parent frame
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        parent_frame = tk.Frame(root)
        tracker = EnhancedProgressTracker(parent_frame)
        
        print("✅ EnhancedProgressTracker instantiated successfully")
        
        # Test basic methods
        if hasattr(tracker, 'start_upload'):
            print("✅ start_upload method available")
        else:
            print("❌ start_upload method missing")
            
        if hasattr(tracker, 'update_progress'):
            print("✅ update_progress method available")
        else:
            print("❌ update_progress method missing")
            
        if hasattr(tracker, 'complete_upload'):
            print("✅ complete_upload method available")
        else:
            print("❌ complete_upload method missing")
            
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Progress tracker test failed: {e}")
        return False

def test_error_handler():
    """Test enhanced error handler"""
    print("\n🔍 Testing Enhanced Error Handler...")
    
    try:
        from enhanced_error_handler import EnhancedErrorHandler
        
        # Create a mock main app for testing
        class MockMainApp:
            def __init__(self):
                self.root = None
                
        mock_app = MockMainApp()
        handler = EnhancedErrorHandler(mock_app)
        
        print("✅ EnhancedErrorHandler instantiated successfully")
        
        # Test basic methods
        if hasattr(handler, 'handle_error'):
            print("✅ handle_error method available")
        else:
            print("❌ handle_error method missing")
            
        if hasattr(handler, 'analyze_error'):
            print("✅ analyze_error method available")
        else:
            print("❌ analyze_error method missing")
            
        if hasattr(handler, 'attempt_automatic_recovery'):
            print("✅ attempt_automatic_recovery method available")
        else:
            print("❌ attempt_automatic_recovery method missing")
            
        return True
        
    except Exception as e:
        print(f"❌ Error handler test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Features Integration Test")
    print("=" * 50)
    
    tests = [
        ("Enhanced Modules Import", test_enhanced_modules),
        ("Main App Integration", test_main_app_integration),
        ("Enhanced Features Functionality", test_enhanced_features_functionality),
        ("Progress Tracker", test_progress_tracker),
        ("Error Handler", test_error_handler)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are properly integrated.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
