#!/usr/bin/env python3
"""
Test script for esptool reset functionality
This script helps test different esptool reset options
"""

import subprocess
import sys

def test_esptool_reset_options():
    """Test different esptool reset options"""
    print("🔧 Testing esptool reset options")
    print("=" * 50)
    
    # Test different reset combinations
    reset_combinations = [
        ("default-reset", "hard-reset", "Standard auto-flash"),
        ("no-reset", "hard-reset", "Manual reset before upload"),
        ("usb-reset", "hard-reset", "USB reset (ESP32 only)"),
        ("no-reset", "no-reset", "No reset at all"),
        ("default-reset", "soft-reset", "Soft reset after upload")
    ]
    
    for before_reset, after_reset, description in reset_combinations:
        print(f"\n🔄 Testing: {description}")
        print(f"   --before {before_reset} --after {after_reset}")
        
        try:
            # Test with chip_id command (safe to run)
            cmd = ["python", "-m", "esptool", "--before", before_reset, "--after", after_reset, "chip_id"]
            print(f"   Command: {' '.join(cmd)}")
            
            # Note: This will fail without a device connected, but we're testing the command syntax
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("   ✅ Command executed successfully")
                if "Chip ID:" in result.stdout:
                    print("   🎉 Device detected and in flash mode!")
                else:
                    print("   ⚠️ Command succeeded but no chip ID found")
            else:
                print(f"   ❌ Command failed (expected without device): {result.stderr.strip()}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n🔍 Reset Option Explanations:")
    print("   default-reset: Uses DTR/RTS lines to reset into bootloader")
    print("   no-reset: Skips reset, useful if hardware isn't wired for reset")
    print("   usb-reset: USB reset (ESP32 only)")
    print("   hard-reset: Hard reset via DTR/RTS after upload")
    print("   soft-reset: Soft reset after upload")
    print("   no-reset (after): No reset after upload")

def test_esptool_availability():
    """Test if esptool is available and working"""
    print("\n🔍 Testing esptool availability")
    print("=" * 40)
    
    try:
        # Test basic esptool command
        result = subprocess.run(["python", "-m", "esptool", "--help"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ esptool is available and working")
            if "esptool" in result.stdout:
                print("✅ esptool help command successful")
            else:
                print("⚠️ esptool help command returned unexpected output")
        else:
            print("❌ esptool help command failed")
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing esptool: {str(e)}")

def main():
    """Main test function"""
    print("🚀 esptool Reset Options Test")
    print("=" * 50)
    
    # Test esptool availability first
    test_esptool_availability()
    
    # Test reset options
    test_esptool_reset_options()
    
    print("\n🎯 Next Steps:")
    print("   1. Connect your ESP8266/ESP32 device")
    print("   2. Run the main application: python j_tech_pixel_uploader.py")
    print("   3. Try the '🔧 esptool Reset' button")
    print("   4. Adjust reset options in Settings → esptool Reset Options")
    print("   5. Test different reset combinations for your hardware")

if __name__ == "__main__":
    main()
