#!/usr/bin/env python3
"""
Test script for .dat file upload functionality
This script tests the new .dat file support in the J Tech Pixel Uploader
"""

import os
import sys
import utils

def test_dat_file_creation():
    """Test creation of .dat pattern files"""
    print("🎨 Testing .dat File Creation...")
    
    try:
        # Create sample .dat files
        created_files = utils.create_sample_dat_files()
        
        if created_files:
            print(f"✅ Created {len(created_files)} .dat pattern files:")
            for filename in created_files:
                filepath = os.path.join("SampleFirmware", filename)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    print(f"   📁 {filename} ({file_size} bytes)")
                else:
                    print(f"   ❌ {filename} - file not found")
        else:
            print("❌ Failed to create .dat files")
            
    except Exception as e:
        print(f"❌ Error creating .dat files: {e}")
    
    print()

def test_dat_file_validation():
    """Test .dat file validation"""
    print("🔍 Testing .dat File Validation...")
    
    # Test with sample .dat files
    sample_dir = "SampleFirmware"
    if os.path.exists(sample_dir):
        dat_files = [f for f in os.listdir(sample_dir) if f.endswith('.dat')]
        
        for dat_file in dat_files[:3]:  # Test first 3 files
            filepath = os.path.join(sample_dir, dat_file)
            print(f"📁 Testing: {dat_file}")
            
            # Validate file
            is_valid, message = utils.validate_dat_file(filepath)
            print(f"   Validation: {'✅' if is_valid else '❌'} {message}")
            
            # Get file info
            file_info = utils.get_dat_file_info(filepath)
            if "error" not in file_info:
                print(f"   Matrix: {file_info['matrix_size']}")
                print(f"   LEDs: {file_info['led_count']}")
                if file_info['rgb_values']:
                    sample = file_info['rgb_values'][0]
                    print(f"   Sample RGB: R={sample[0]}, G={sample[1]}, B={sample[2]}")
            else:
                print(f"   Error: {file_info['error']}")
            print()
    else:
        print("❌ SampleFirmware directory not found")
    
    print()

def test_invalid_dat_files():
    """Test validation with invalid .dat files"""
    print("🚫 Testing Invalid .dat File Detection...")
    
    # Create a test invalid file
    test_file = "test_invalid.dat"
    try:
        # Create file with invalid data
        with open(test_file, 'wb') as f:
            f.write(b'\xFF\xFF\xFF\x00\x01\x02\x03')  # Invalid size (not multiple of 3)
        
        print(f"📁 Testing invalid file: {test_file}")
        
        # Test validation
        is_valid, message = utils.validate_dat_file(test_file)
        print(f"   Validation: {'✅' if is_valid else '❌'} {message}")
        
        # Test file info
        file_info = utils.get_dat_file_info(test_file)
        if "error" not in file_info:
            print(f"   Matrix: {file_info['matrix_size']}")
            print(f"   LEDs: {file_info['led_count']}")
        else:
            print(f"   Error: {file_info['error']}")
        
        # Clean up
        os.remove(test_file)
        print(f"   🗑️ Cleaned up test file")
        
    except Exception as e:
        print(f"❌ Error testing invalid file: {e}")
    
    print()

def test_protocol_packet_creation():
    """Test LED pattern protocol packet creation"""
    print("📦 Testing Protocol Packet Creation...")
    
    try:
        # Create a simple test pattern
        test_pattern = utils.create_heart_pattern()
        
        # Simulate protocol packet creation (like in the uploader)
        header = b'LEDP'  # LED Pattern identifier
        data_length = len(test_pattern).to_bytes(4, 'little')
        checksum = sum(test_pattern) & 0xFF
        
        packet = header + data_length + test_pattern + bytes([checksum])
        
        print(f"✅ Protocol packet created successfully:")
        print(f"   Header: {header}")
        print(f"   Data length: {len(test_pattern)} bytes")
        print(f"   Checksum: 0x{checksum:02X}")
        print(f"   Total packet size: {len(packet)} bytes")
        print(f"   Pattern: Heart shape ({len(test_pattern)//3} LEDs)")
        
    except Exception as e:
        print(f"❌ Error testing protocol: {e}")
    
    print()

def main():
    """Main test function"""
    print("🎯 .dat File Upload Functionality Test")
    print("=" * 50)
    
    # Test .dat file creation
    test_dat_file_creation()
    
    # Test file validation
    test_dat_file_validation()
    
    # Test invalid file detection
    test_invalid_dat_files()
    
    # Test protocol packet creation
    test_protocol_packet_creation()
    
    print("🎉 .dat file functionality test completed!")
    print("\n💡 To test the full functionality:")
    print("   1. Run the main application: python j_tech_pixel_uploader.py")
    print("   2. Click 'Create Sample Patterns' button")
    print("   3. Select a .dat pattern file")
    print("   4. Use 'Upload Firmware' button (it will detect .dat and use pattern protocol)")
    print("   5. Check the log for pattern upload details")

if __name__ == "__main__":
    main()
