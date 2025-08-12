#!/usr/bin/env python3
"""
Verify ESP8266 Firmware Upload - Check if new firmware is running
"""

import serial
import time
import sys

def verify_firmware(port="COM5", baud=115200, timeout=10):
    """Verify the uploaded firmware is working"""
    print(f"🔍 Verifying firmware on {port} at {baud} baud...")
    print("=" * 50)
    
    try:
        # Open serial connection
        ser = serial.Serial(port, baud, timeout=timeout)
        print(f"✅ Connected to {port}")
        
        # Wait for any boot messages
        print("⏳ Waiting for boot messages...")
        time.sleep(2)
        
        # Read any available data
        if ser.in_waiting > 0:
            boot_data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print("📡 Boot messages received:")
            print("-" * 30)
            print(boot_data)
            print("-" * 30)
        
        # Send test commands to see device response
        test_commands = [
            b'\r\n',           # Enter key
            b'help\r\n',       # Help command
            b'version\r\n',    # Version command
            b'info\r\n',       # Info command
            b'status\r\n',     # Status command
        ]
        
        print("\n🧪 Testing device responses...")
        for i, cmd in enumerate(test_commands, 1):
            print(f"   Test {i}: Sending '{cmd.decode().strip()}'...")
            
            # Send command
            ser.write(cmd)
            time.sleep(0.5)
            
            # Read response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if response.strip():
                    print(f"      ✅ Response: {response.strip()}")
                else:
                    print(f"      ⚠️ No response")
            else:
                print(f"      ⚠️ No response")
            
            time.sleep(0.5)
        
        # Try to detect what type of firmware is running
        print("\n🔍 Analyzing firmware type...")
        
        # Send a few more diagnostic commands
        diagnostic_commands = [
            b'ls\r\n',         # List files (if filesystem)
            b'free\r\n',       # Memory info
            b'uptime\r\n',     # Uptime
            b'reset\r\n',      # Soft reset
        ]
        
        for cmd in diagnostic_commands:
            ser.write(cmd)
            time.sleep(0.3)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                if response.strip():
                    print(f"   {cmd.decode().strip()}: {response.strip()}")
        
        ser.close()
        
        print("\n✅ Firmware verification completed!")
        print("💡 If you see responses above, your firmware is working!")
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        print("💡 Make sure:")
        print("   • ESP8266 is connected")
        print("   • Correct COM port selected")
        print("   • Device is powered on")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_esptool_connection(port="COM5"):
    """Check if esptool can still communicate with the device"""
    print(f"\n🔧 Testing esptool communication on {port}...")
    
    try:
        import subprocess
        
        # Try to get chip info
        cmd = ["python", "-m", "esptool", "--port", port, "--chip", "esp8266", "--before", "no-reset", "--after", "no-reset", "chip_id"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ esptool communication successful!")
            print("📋 Device info:")
            print(result.stdout)
            
            if "Chip ID:" in result.stdout:
                print("🎉 Your ESP8266 is responding and ready for future uploads!")
            else:
                print("⚠️ Device responded but no chip ID found")
        else:
            print("❌ esptool communication failed")
            print("📋 Error output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ esptool test failed: {e}")

def main():
    """Main verification function"""
    print("🚀 ESP8266 Firmware Upload Verification")
    print("=" * 50)
    
    port = input("Enter COM port (default: COM5): ").strip() or "COM5"
    
    # Method 1: Serial monitor verification
    print(f"\n1️⃣ Serial Monitor Verification...")
    verify_firmware(port)
    
    # Method 2: esptool communication test
    print(f"\n2️⃣ esptool Communication Test...")
    check_esptool_connection(port)
    
    print("\n" + "=" * 50)
    print("🏁 Verification completed!")
    print("\n💡 What to look for:")
    print("   • Boot messages (indicates firmware is running)")
    print("   • Command responses (shows firmware is interactive)")
    print("   • esptool communication (confirms device is accessible)")
    print("   • Any error messages (helps identify issues)")

if __name__ == "__main__":
    main()

