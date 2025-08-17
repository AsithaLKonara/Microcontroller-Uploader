#!/usr/bin/env python3
"""
Test script for HEX to BIN conversion
"""

import os
import tempfile
import utils

def test_hex_conversion():
    """Test HEX to BIN conversion with a simple file"""
    print("Testing HEX to BIN conversion...")
    
    # Check if converter is available
    converter = utils.find_hex_converter()
    if not converter:
        print("No HEX converter available")
        return False
    
    print(f"Found converter: {converter}")
    
    # Create test HEX file
    test_dir = tempfile.mkdtemp(prefix="test_hex_")
    hex_file = os.path.join(test_dir, "test.hex")
    
    # Create a simple HEX file with proper Intel HEX format
    with open(hex_file, 'w') as f:
        f.write(":020000040000FA\n")  # Extended linear address
        f.write(":100000000102030405060708090A0B0C0D0E0F10\n")  # Data line (16 bytes)
        f.write(":100010001112131415161718191A1B1C1D1E1F20\n")  # More data
        f.write(":00000001FF\n")  # End of file
    
    print(f"Created test HEX file: {hex_file}")
    
    # Test conversion
    success, output_path, error_msg = utils.convert_hex_to_bin(hex_file)
    
    if success:
        print(f"✅ HEX conversion successful: {output_path}")
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"✅ Output file size: {size} bytes")
        else:
            print("❌ Output file not found")
    else:
        print(f"❌ HEX conversion failed: {error_msg}")
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(test_dir)
    except:
        pass
    
    return success

if __name__ == "__main__":
    test_hex_conversion()
