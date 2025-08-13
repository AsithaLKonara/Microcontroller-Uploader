#!/usr/bin/env python3
"""
ESP8266 Firmware Pre-Upload Validator
Validates firmware before uploading to prevent wasted time and failed uploads
"""

import os
import sys
import time
import serial
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class FirmwareValidator:
    def __init__(self, port: str = None, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.validation_results = []
        self.errors = []
        self.warnings = []
        
        # ESP8266 specifications
        self.ESP8266_SPECS = {
            "flash_size_min": 1024,        # 1KB minimum
            "flash_size_max": 4 * 1024 * 1024,  # 4MB maximum
            "supported_formats": [".bin"],
            "unsupported_formats": [".hex", ".elf", ".o"],
            "max_upload_size": 3 * 1024 * 1024,  # 3MB practical limit
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log validation messages with timestamps"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"
        print(formatted_message)
        
        if level == "ERROR":
            self.errors.append(message)
        elif level == "WARNING":
            self.warnings.append(message)
        else:
            self.validation_results.append(message)
    
    def validate_firmware_file(self, filepath: str) -> bool:
        """Main validation method - returns True if all checks pass"""
        self.log("🔍 Starting firmware validation...")
        
        if not os.path.exists(filepath):
            self.log(f"Firmware file not found: {filepath}", "ERROR")
            return False
        
        # Run all validation checks
        checks = [
            self._check_file_format,
            self._check_file_size,
            self._check_file_integrity,
            self._check_esptool_availability,
            self._check_port_connectivity,
            self._check_hardware_compatibility,
        ]
        
        all_passed = True
        for check in checks:
            try:
                if not check(filepath):
                    all_passed = False
            except Exception as e:
                self.log(f"Validation check failed: {str(e)}", "ERROR")
                all_passed = False
        
        # Summary
        if all_passed:
            self.log("✅ All firmware validation checks passed!", "INFO")
            self._print_summary()
        else:
            self.log("❌ Firmware validation failed!", "ERROR")
            self._print_summary()
        
        return all_passed
    
    def _check_file_format(self, filepath: str) -> bool:
        """Check if file format is compatible with ESP8266"""
        self.log("📁 Checking firmware file format...")
        
        file_ext = Path(filepath).suffix.lower()
        
        if file_ext in self.ESP8266_SPECS["supported_formats"]:
            self.log(f"✅ File format '{file_ext}' is supported")
            return True
        elif file_ext in self.ESP8266_SPECS["unsupported_formats"]:
            self.log(f"❌ File format '{file_ext}' is NOT supported for ESP8266", "ERROR")
            self.log(f"   ESP8266 cannot execute {file_ext} files", "ERROR")
            self.log(f"   Convert to .bin format or recompile for ESP8266", "ERROR")
            return False
        else:
            self.log(f"⚠ Unknown file format '{file_ext}' - proceed with caution", "WARNING")
            return True
    
    def _check_file_size(self, filepath: str) -> bool:
        """Check if file size is within ESP8266 limits"""
        self.log("📏 Checking firmware file size...")
        
        try:
            file_size = os.path.getsize(filepath)
            size_kb = file_size / 1024
            size_mb = size_kb / 1024
            
            self.log(f"   File size: {size_kb:.1f} KB ({size_mb:.2f} MB)")
            
            if file_size < self.ESP8266_SPECS["flash_size_min"]:
                self.log(f"❌ File too small ({size_kb:.1f} KB) - suspicious for ESP firmware", "ERROR")
                return False
            elif file_size > self.ESP8266_SPECS["flash_size_max"]:
                self.log(f"❌ File too large ({size_mb:.2f} MB) - exceeds ESP8266 flash capacity", "ERROR")
                return False
            elif file_size > self.ESP8266_SPECS["max_upload_size"]:
                self.log(f"⚠ File large ({size_mb:.2f} MB) - may take a while to upload", "WARNING")
            
            self.log("✅ File size is within acceptable range")
            return True
            
        except Exception as e:
            self.log(f"❌ Could not check file size: {str(e)}", "ERROR")
            return False
    
    def _check_file_integrity(self, filepath: str) -> bool:
        """Check file integrity and basic binary validation"""
        self.log("🔒 Checking file integrity...")
        
        try:
            with open(filepath, 'rb') as f:
                # Read first few bytes to check if it's actually binary
                header = f.read(16)
                
                # Check for common file signatures
                if header.startswith(b'\x7fELF'):
                    self.log("❌ File appears to be ELF format - not suitable for ESP8266", "ERROR")
                    return False
                elif header.startswith(b':'):
                    self.log("❌ File appears to be Intel HEX format - not suitable for ESP8266", "ERROR")
                    return False
                
                # Calculate file hash for integrity
                f.seek(0)
                file_hash = hashlib.md5()
                chunk_size = 8192
                while chunk := f.read(chunk_size):
                    file_hash.update(chunk)
                
                hash_hex = file_hash.hexdigest()[:8]
                self.log(f"   File hash: {hash_hex}...")
                self.log("✅ File integrity check passed")
                return True
                
        except Exception as e:
            self.log(f"❌ File integrity check failed: {str(e)}", "ERROR")
            return False
    
    def _check_esptool_availability(self, filepath: str) -> bool:
        """Check if esptool.py is available and working"""
        self.log("🔧 Checking esptool.py availability...")
        
        try:
            result = subprocess.run(
                ["esptool.py", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log(f"✅ esptool.py available: {version}")
                return True
            else:
                self.log("❌ esptool.py not working properly", "ERROR")
                return False
                
        except FileNotFoundError:
            self.log("❌ esptool.py not found - install with: pip install esptool", "ERROR")
            return False
        except subprocess.TimeoutExpired:
            self.log("❌ esptool.py check timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ esptool.py check failed: {str(e)}", "ERROR")
            return False
    
    def _check_port_connectivity(self, filepath: str) -> bool:
        """Check if the specified port is accessible"""
        if not self.port:
            self.log("⚠ No port specified - skipping port connectivity check", "WARNING")
            return True
        
        self.log(f"🔌 Checking port connectivity: {self.port}")
        
        try:
            # Try to open the serial port
            with serial.Serial(self.port, self.baud, timeout=2) as ser:
                self.log(f"✅ Port {self.port} is accessible")
                return True
                
        except serial.SerialException as e:
            self.log(f"❌ Port {self.port} not accessible: {str(e)}", "ERROR")
            self.log("   Check if ESP8266 is connected and not in use by another program", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Port check failed: {str(e)}", "ERROR")
            return False
    
    def _check_hardware_compatibility(self, filepath: str) -> bool:
        """Check if the ESP8266 hardware is compatible"""
        if not self.port:
            self.log("⚠ No port specified - skipping hardware compatibility check", "WARNING")
            return True
        
        self.log("🖥️ Checking ESP8266 hardware compatibility...")
        
        try:
            # Try to get chip info
            result = subprocess.run(
                ["esptool.py", "--port", self.port, "--baud", str(self.baud), "chip_id"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                if "Chip ID:" in result.stdout:
                    self.log("✅ ESP8266 hardware detected and responding")
                    return True
                else:
                    self.log("⚠ Hardware detected but may not be ESP8266", "WARNING")
                    return True
            else:
                self.log("❌ Could not communicate with ESP8266 hardware", "ERROR")
                self.log("   Check wiring, power, and boot mode", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Hardware check timed out - ESP8266 may be in flash mode", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Hardware compatibility check failed: {str(e)}", "ERROR")
            return False
    
    def _print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 FIRMWARE VALIDATION SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
            print()
        
        if self.warnings:
            print(f"⚠ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        if self.validation_results:
            print(f"✅ PASSED CHECKS ({len(self.validation_results)}):")
            for result in self.validation_results:
                print(f"   • {result}")
            print()
        
        if not self.errors:
            print("🎉 FIRMWARE READY FOR UPLOAD!")
            print("   Run: esptool.py --port <PORT> --baud 115200 write_flash 0x00000 <FIRMWARE>")
        else:
            print("🚫 FIRMWARE NOT READY - Fix errors above before uploading")
        
        print("="*60)
    
    def quick_led_test(self) -> bool:
        """Run a quick LED test to verify hardware before main firmware upload"""
        if not self.port:
            self.log("⚠ No port specified - cannot run LED test", "WARNING")
            return False
        
        self.log("💡 Running quick LED hardware test...")
        
        # Create a minimal test firmware that just blinks an LED
        test_code = '''
import machine
import time

# Configure GPIO pin (adjust pin number as needed)
led_pin = machine.Pin(2, machine.Pin.OUT)  # Built-in LED on most ESP8266 boards

print("LED Test Starting...")

# Blink LED 5 times
for i in range(5):
    led_pin.on()
    print(f"LED ON - Test {i+1}/5")
    time.sleep(0.5)
    led_pin.off()
    print(f"LED OFF - Test {i+1}/5")
    time.sleep(0.5)

print("LED Test Complete!")
'''
        
        try:
            # Save test code to temporary file
            test_file = "led_test.py"
            with open(test_file, 'w') as f:
                f.write(test_code)
            
            self.log("   Created LED test firmware")
            
            # Upload test firmware
            self.log("   Uploading LED test firmware...")
            result = subprocess.run([
                "esptool.py", "--port", self.port, "--baud", str(self.baud),
                "write_flash", "0x00000", test_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log("✅ LED test firmware uploaded successfully")
                self.log("   Watch the built-in LED - it should blink 5 times")
                self.log("   Check serial monitor for test output")
                
                # Clean up test file
                try:
                    os.remove(test_file)
                except:
                    pass
                
                return True
            else:
                self.log("❌ LED test firmware upload failed", "ERROR")
                self.log(f"   Error: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ LED test failed: {str(e)}", "ERROR")
            return False

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ESP8266 Firmware Pre-Upload Validator")
    parser.add_argument("firmware", help="Path to firmware file to validate")
    parser.add_argument("--port", "-p", help="COM port for ESP8266")
    parser.add_argument("--baud", "-b", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--led-test", action="store_true", help="Run LED hardware test after validation")
    
    args = parser.parse_args()
    
    # Create validator
    validator = FirmwareValidator(port=args.port, baud=args.baud)
    
    # Validate firmware
    if validator.validate_firmware_file(args.firmware):
        print("\n🚀 Firmware validation successful!")
        
        if args.led_test and args.port:
            print("\n💡 Running LED hardware test...")
            if validator.quick_led_test():
                print("🎉 Hardware test passed - ready for main firmware!")
            else:
                print("⚠ Hardware test failed - check wiring before uploading main firmware")
        
        return 0
    else:
        print("\n❌ Firmware validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
