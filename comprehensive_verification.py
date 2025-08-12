#!/usr/bin/env python3
"""
Comprehensive ESP8266 Firmware Verification
"""

import serial
import time
import subprocess

def test_multiple_baud_rates(port="COM5"):
    """Test communication at different baud rates"""
    print(f"🔍 Testing multiple baud rates on {port}...")
    print("=" * 50)
    
    baud_rates = [9600, 19200, 38400, 57600, 74880, 115200, 230400, 460800]
    
    for baud in baud_rates:
        print(f"\n📡 Testing {baud} baud...")
        try:
            ser = serial.Serial(port, baud, timeout=2)
            
            # Wait a bit for any startup messages
            time.sleep(1)
            
            # Check for any data
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if data.strip():
                    print(f"   ✅ Data received: {data.strip()}")
                else:
                    print(f"   ⚠️ No data")
            else:
                print(f"   ⚠️ No data")
            
            # Try sending a simple command
            ser.write(b'\r\n')
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if response.strip():
                    print(f"   ✅ Response to Enter: {response.strip()}")
                else:
                    print(f"   ⚠️ No response to Enter")
            else:
                print(f"   ⚠️ No response to Enter")
            
            ser.close()
            
        except Exception as e:
            print(f"   ❌ Error at {baud} baud: {e}")

def check_device_power_cycle(port="COM5"):
    """Check if device responds after power cycle simulation"""
    print(f"\n🔄 Testing device power cycle response on {port}...")
    print("=" * 50)
    
    try:
        # Try to open port
        ser = serial.Serial(port, 115200, timeout=1)
        print("✅ Port opened successfully")
        
        # Simulate power cycle by closing and reopening
        ser.close()
        time.sleep(1)
        
        ser = serial.Serial(port, 115200, timeout=2)
        print("✅ Port reopened after 'power cycle'")
        
        # Wait for any boot messages
        print("⏳ Waiting for boot messages...")
        time.sleep(3)
        
        if ser.in_waiting > 0:
            boot_data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if boot_data.strip():
                print("📡 Boot messages detected:")
                print("-" * 30)
                print(boot_data)
                print("-" * 30)
            else:
                print("⚠️ No boot messages detected")
        else:
            print("⚠️ No boot messages detected")
        
        ser.close()
        
    except Exception as e:
        print(f"❌ Power cycle test failed: {e}")

def test_esptool_recovery(port="COM5"):
    """Test if we can put device back in flash mode"""
    print(f"\n🔧 Testing esptool recovery on {port}...")
    print("=" * 50)
    
    try:
        # Try to get chip info without reset
        cmd = ["python", "-m", "esptool", "--port", port, "--chip", "esp8266", "--before", "no-reset", "--after", "no-reset", "chip_id"]
        
        print("📡 Testing current device state...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Device is accessible via esptool!")
            print("📋 Device info:")
            print(result.stdout)
        else:
            print("⚠️ Device not accessible via esptool (normal when running firmware)")
            print("📋 Error output:")
            print(result.stderr)
            
            # Try with reset
            print("\n🔄 Trying with reset...")
            cmd_reset = ["python", "-m", "esptool", "--port", port, "--chip", "esp8266", "--before", "default-reset", "--after", "hard-reset", "chip_id"]
            
            result_reset = subprocess.run(cmd_reset, capture_output=True, text=True, timeout=15)
            
            if result_reset.returncode == 0:
                print("✅ Device recovered and accessible!")
                print("📋 Device info:")
                print(result_reset.stdout)
            else:
                print("❌ Device still not accessible")
                print("📋 Error output:")
                print(result_reset.stderr)
                
    except Exception as e:
        print(f"❌ esptool recovery test failed: {e}")

def main():
    """Main verification function"""
    print("🚀 Comprehensive ESP8266 Firmware Verification")
    print("=" * 60)
    
    port = input("Enter COM port (default: COM5): ").strip() or "COM5"
    
    # Test 1: Multiple baud rates
    test_multiple_baud_rates(port)
    
    # Test 2: Power cycle simulation
    check_device_power_cycle(port)
    
    # Test 3: esptool recovery
    test_esptool_recovery(port)
    
    print("\n" + "=" * 60)
    print("🏁 Comprehensive verification completed!")
    print("\n💡 Interpretation Guide:")
    print("   ✅ SUCCESS indicators:")
    print("      • Any serial data received")
    print("      • Device responds to commands")
    print("      • Boot messages visible")
    print("      • esptool can communicate")
    print("\n   ⚠️ NORMAL behavior:")
    print("      • No serial output (many firmwares are silent)")
    print("      • No command responses (no interactive shell)")
    print("      • esptool can't connect (device running firmware)")
    print("\n   🎯 Your upload was SUCCESSFUL if:")
    print("      • Upload completed without errors")
    print("      • Hash verification passed")
    print("      • Device reset completed")
    print("      • No more 'Failed to connect' errors")

if __name__ == "__main__":
    main()

