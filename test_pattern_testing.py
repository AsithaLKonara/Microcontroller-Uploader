#!/usr/bin/env python3
"""
Test script for LED Pattern Testing functionality
This script tests the pattern detection and creation functions
"""

import os
import sys
import utils

def test_pattern_detection():
    """Test LED pattern detection functionality"""
    print("🧪 Testing LED Pattern Detection...")
    
    # Test with sample patterns
    test_files = [
        "SampleFirmware/alternating_cols_8x8.bin",
        "SampleFirmware/checkerboard_8x8.bin",
        "SampleFirmware/rainbow_8x8.bin"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"📁 Testing: {test_file}")
            # This would normally be called from the main app
            print(f"   ✅ File exists and ready for testing")
        else:
            print(f"📁 Testing: {test_file}")
            print(f"   ❌ File not found")
    
    print()

def test_pattern_creation():
    """Test LED pattern creation functionality"""
    print("🎨 Testing LED Pattern Creation...")
    
    try:
        # Create sample patterns
        created_files = utils.create_sample_led_patterns()
        
        if created_files:
            print(f"✅ Successfully created {len(created_files)} pattern files:")
            for filename in created_files:
                filepath = os.path.join("SampleFirmware", filename)
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"   📁 {filename} ({size} bytes)")
                else:
                    print(f"   ❌ {filename} (file not found)")
        else:
            print("❌ No pattern files were created")
            
    except Exception as e:
        print(f"❌ Error creating patterns: {e}")
    
    print()

def test_custom_protocol():
    """Test custom protocol simulation"""
    print("📡 Testing Custom Protocol Simulation...")
    
    # Simulate protocol packet creation
    try:
        # Create a test pattern
        test_pattern = utils.create_alternating_cols_pattern()
        
        # Simulate protocol packet
        header = b'LEDP'  # LED Pattern identifier
        data_length = len(test_pattern).to_bytes(4, 'little')
        checksum = sum(test_pattern) & 0xFF
        
        packet = header + data_length + test_pattern + bytes([checksum])
        
        print(f"✅ Protocol packet created successfully:")
        print(f"   Header: {header}")
        print(f"   Data length: {len(test_pattern)} bytes")
        print(f"   Checksum: 0x{checksum:02X}")
        print(f"   Total packet size: {len(packet)} bytes")
        
    except Exception as e:
        print(f"❌ Error testing protocol: {e}")
    
    print()

def main():
    """Main test function"""
    print("🎯 LED Pattern Testing - Functionality Test")
    print("=" * 50)
    
    # Test pattern creation first
    test_pattern_creation()
    
    # Test pattern detection
    test_pattern_detection()
    
    # Test custom protocol
    test_custom_protocol()
    
    print("🎉 Pattern testing functionality test completed!")
    print("\n💡 To test the full functionality:")
    print("   1. Run the main application: python j_tech_pixel_uploader.py")
    print("   2. Click 'Create Sample Patterns' button")
    print("   3. Select a sample pattern file")
    print("   4. Enable 'Pattern Testing' mode")
    print("   5. Use 'Test Pattern' or 'Verify Hardware' buttons")

if __name__ == "__main__":
    main()
