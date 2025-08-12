#!/usr/bin/env python3
"""
Hardware Reset Debug Tool
This script helps diagnose hardware reset issues with ESP8266/ESP32 boards
"""

import serial
import serial.tools.list_ports
import time
import sys

def list_available_ports():
    """List all available COM ports with detailed information"""
    print("🔍 Available COM Ports:")
    print("=" * 50)
    
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("❌ No COM ports found!")
        return []
    
    for i, port in enumerate(ports):
        print(f"Port {i+1}: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  Product: {port.product}")
        print(f"  VID:PID: {port.vid:04x}:{port.pid:04x}")
        print()
    
    return ports

def test_port_access(port_name):
    """Test if we can access a specific port"""
    print(f"🔧 Testing port access: {port_name}")
    print("=" * 40)
    
    try:
        # Try to open the port
        ser = serial.Serial(port_name, 115200, timeout=1)
        print("✅ Port opened successfully")
        
        # Test DTR/RTS control
        print("🔄 Testing DTR/RTS control...")
        
        # Test DTR
        ser.setDTR(False)
        time.sleep(0.1)
        ser.setDTR(True)
        print("✅ DTR control working")
        
        # Test RTS
        ser.setRTS(False)
        time.sleep(0.1)
        ser.setRTS(True)
        print("✅ RTS control working")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_esp_reset_sequences(port_name):
    """Test different ESP reset sequences"""
    print(f"🚀 Testing ESP reset sequences on {port_name}")
    print("=" * 50)
    
    sequences = [
        ("Standard ESP Reset", [
            (False, False, 0.1),
            (True, False, 0.1),
            (False, True, 0.1),
            (True, False, 0.1)
        ]),
        ("Single Button Reset", [
            (False, False, 0.5),
            (True, False, 0.3),
            (False, True, 0.5),
            (True, False, 0.3)
        ]),
        ("CH340 Reset", [
            (False, False, 0.2),
            (True, False, 0.2),
            (False, True, 0.3),
            (True, False, 0.2)
        ]),
        ("Aggressive Reset", [
            (False, False, 0.05),
            (True, False, 0.05),
            (False, True, 0.05),
            (True, False, 0.05)
        ])
    ]
    
    for seq_name, steps in sequences:
        print(f"\n🔄 Testing: {seq_name}")
        try:
            ser = serial.Serial(port_name, 74880, timeout=1)
            
            for i, (dtr, rts, delay) in enumerate(steps):
                ser.setDTR(dtr)
                ser.setRTS(rts)
                time.sleep(delay)
                print(f"  Step {i+1}: DTR={dtr}, RTS={rts}, Delay={delay}s")
            
            ser.close()
            print(f"✅ {seq_name} completed successfully")
            
        except Exception as e:
            print(f"❌ {seq_name} failed: {e}")

def test_baud_rate_compatibility(port_name):
    """Test different baud rates for compatibility"""
    print(f"📡 Testing baud rate compatibility on {port_name}")
    print("=" * 50)
    
    baud_rates = [74880, 115200, 57600, 38400, 9600]
    
    for baud in baud_rates:
        try:
            ser = serial.Serial(port_name, baud, timeout=1)
            print(f"✅ {baud} baud: OK")
            
            # Try to send a simple command
            ser.write(b'\x00')
            time.sleep(0.1)
            
            ser.close()
            
        except Exception as e:
            print(f"❌ {baud} baud: {e}")

def test_esptool_communication(port_name):
    """Test if esptool can communicate with the device"""
    print(f"🔧 Testing esptool communication on {port_name}")
    print("=" * 50)
    
    try:
        import subprocess
        
        # Test chip_id command
        cmd = ["python", "-m", "esptool", "--port", port_name, "chip_id"]
        print(f"Executing: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ esptool communication successful!")
            print("Output:")
            print(result.stdout)
        else:
            print("❌ esptool communication failed!")
            print("Error output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error testing esptool: {e}")

def main():
    """Main diagnostic function"""
    print("🔧 Hardware Reset Debug Tool")
    print("=" * 50)
    print("This tool will help diagnose hardware reset issues")
    print()
    
    # List available ports
    ports = list_available_ports()
    if not ports:
        return
    
    # Ask user to select a port
    print("Select a COM port to test:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    
    try:
        choice = int(input("\nEnter port number (or 0 to test all): ")) - 1
        
        if choice == 0:
            # Test all ports
            for port in ports:
                print(f"\n{'='*60}")
                print(f"Testing {port.device}")
                print(f"{'='*60}")
                
                if test_port_access(port.device):
                    test_esp_reset_sequences(port.device)
                    test_baud_rate_compatibility(port.device)
                    test_esptool_communication(port.device)
                
                print(f"\nCompleted testing {port.device}")
                print("=" * 60)
                
        elif 0 <= choice < len(ports):
            # Test specific port
            selected_port = ports[choice].device
            print(f"\nTesting port: {selected_port}")
            
            if test_port_access(selected_port):
                test_esp_reset_sequences(selected_port)
                test_baud_rate_compatibility(selected_port)
                test_esptool_communication(selected_port)
        else:
            print("Invalid choice!")
            
    except ValueError:
        print("Invalid input! Please enter a number.")
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
    
    print("\n🔍 Diagnostic completed!")
    print("\n💡 Common solutions for hardware reset issues:")
    print("   1. Try different USB cables")
    print("   2. Try different USB ports")
    print("   3. Update USB-to-serial drivers")
    print("   4. Check if device has physical FLASH button")
    print("   5. Try manual reset sequence: Hold RESET, press FLASH, release RESET")

if __name__ == "__main__":
    main()
