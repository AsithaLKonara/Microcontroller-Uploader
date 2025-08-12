#!/usr/bin/env python3
"""
Test script for ESP-01 reset methods
"""

import serial
import time
import subprocess

def test_esp01_aggressive_reset(port="COM5"):
    """Test the aggressive ESP-01 reset method"""
    print(f"🔥 Testing ESP-01 Aggressive Reset on {port}...")
    
    try:
        # Phase 1: Multiple DTR/RTS cycles
        print("   🔄 Phase 1: Multiple DTR/RTS cycles...")
        for i in range(5):
            print(f"      Cycle {i+1}/5...")
            try:
                ser = serial.Serial(port, 74880, timeout=1)
                if ser.is_open:
                    ser.setDTR(False)
                    ser.setRTS(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    ser.setRTS(True)
                    time.sleep(0.1)
                    ser.setDTR(False)
                    ser.setRTS(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    ser.setRTS(True)
                    ser.close()
                    time.sleep(0.5)
                    print(f"         Cycle {i+1} completed")
            except Exception as e:
                print(f"         Cycle {i+1} failed: {e}")
                time.sleep(0.2)
        
        # Phase 2: Baud rate cycling with reset
        print("   🔄 Phase 2: Baud rate cycling with reset...")
        baud_rates = [74880, 115200, 57600, 38400]
        
        for baud in baud_rates:
            print(f"      Trying {baud} baud...")
            try:
                ser = serial.Serial(port, baud, timeout=1)
                if ser.is_open:
                    # Send reset sequence at this baud rate
                    ser.setDTR(False)
                    ser.setRTS(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    ser.setRTS(True)
                    time.sleep(0.1)
                    ser.setDTR(False)
                    ser.setRTS(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    ser.setRTS(True)
                    ser.close()
                    time.sleep(0.5)
                    print(f"         {baud} baud reset completed")
            except Exception as e:
                print(f"         {baud} baud failed: {e}")
                continue
        
        # Phase 3: Extended timing reset
        print("   🔄 Phase 3: Extended timing reset...")
        try:
            ser = serial.Serial(port, 74880, timeout=1)
            if ser.is_open:
                # Hold DTR/RTS low for extended period
                ser.setDTR(False)
                ser.setRTS(False)
                print("         Holding DTR/RTS low for 2 seconds...")
                time.sleep(2)  # Hold for 2 seconds
                ser.setDTR(True)
                ser.setRTS(True)
                time.sleep(1)
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(0.5)
                ser.setDTR(True)
                ser.setRTS(True)
                ser.close()
                print("         Extended reset completed")
        except Exception as e:
            print(f"         Extended reset failed: {e}")
        
        print("✅ ESP-01 aggressive reset sequence completed")
        return True
        
    except Exception as e:
        print(f"❌ Error during ESP-01 aggressive reset: {e}")
        return False

def test_esptool_communication(port="COM5"):
    """Test if esptool can communicate with the device"""
    print(f"🔧 Testing esptool communication on {port}...")
    
    # Try multiple baud rates
    baud_rates = [74880, 115200, 57600, 38400]
    
    for baud in baud_rates:
        print(f"   Trying {baud} baud...")
        try:
            cmd = ["python", "-m", "esptool", "--port", port, "--baud", str(baud), "--chip", "esp8266", "--before", "no-reset", "--after", "no-reset", "chip_id"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Chip ID:" in result.stdout:
                print(f"✅ Communication successful at {baud} baud!")
                print(f"   Output: {result.stdout.strip()}")
                return True
            else:
                print(f"⚠️ Failed at {baud} baud")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout at {baud} baud")
        except Exception as e:
            print(f"⚠️ Error at {baud} baud: {e}")
    
    print("❌ All baud rates failed")
    return False

def test_manual_reset_sequence():
    """Test the manual reset sequence"""
    print("🚨 MANUAL RESET SEQUENCE TEST")
    print("💡 Follow these steps EXACTLY:")
    print("   1. Unplug USB cable completely")
    print("   2. Wait 15 seconds")
    print("   3. Plug USB cable back in")
    print("   4. IMMEDIATELY press and HOLD RESET button")
    print("   5. Keep holding for 10 seconds")
    print("   6. Release RESET button")
    print("   7. Wait 5 seconds")
    print("   8. Press RESET button briefly (0.5 seconds)")
    print("   9. Wait for device to enter flash mode")
    
    input("Press Enter when you've completed the sequence...")
    
    # Test communication
    return test_esptool_communication()

def main():
    """Main test function"""
    port = "COM5"  # Change this to your port
    
    print("🧪 ESP-01 Reset Test Suite")
    print("=" * 50)
    
    # Test 1: Aggressive hardware reset
    print("\n1️⃣ Testing Aggressive Hardware Reset...")
    if test_esp01_aggressive_reset(port):
        print("✅ Hardware reset completed, testing communication...")
        time.sleep(3)
        if test_esptool_communication(port):
            print("🎉 SUCCESS! Hardware reset worked!")
            return
        else:
            print("⚠️ Hardware reset completed but communication failed")
    else:
        print("❌ Hardware reset failed")
    
    # Test 2: Manual reset sequence
    print("\n2️⃣ Testing Manual Reset Sequence...")
    if test_manual_reset_sequence():
        print("🎉 SUCCESS! Manual reset worked!")
        return
    else:
        print("❌ Manual reset failed")
    
    print("\n❌ All reset methods failed")
    print("💡 Your ESP-01 may have hardware issues or need different wiring")

if __name__ == "__main__":
    main()
