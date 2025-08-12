#!/usr/bin/env python3
"""
Enhanced Features for J Tech Pixel Uploader
Adds: Error handling, device detection, progress tracking, validation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
import json
import threading
import serial
import serial.tools.list_ports
from datetime import datetime
import hashlib

class EnhancedFeatures:
    """Enhanced features that can be integrated into the main uploader"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.auto_detection_enabled = True
        self.upload_retry_count = 0
        self.max_retries = 3
        self.upload_start_time = None
        self.device_status = {}
        
        # Start auto-detection
        self.start_auto_detection()
    
    def start_auto_detection(self):
        """Start automatic device detection"""
        if self.auto_detection_enabled:
            self.auto_detection_thread = threading.Thread(target=self.auto_detection_loop, daemon=True)
            self.auto_detection_thread.start()
    
    def auto_detection_loop(self):
        """Continuous auto-detection loop"""
        while self.auto_detection_enabled:
            try:
                self.detect_available_ports()
                self.auto_detect_devices()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                print(f"Auto-detection error: {e}")
                time.sleep(5)
    
    def detect_available_ports(self):
        """Detect available COM ports"""
        try:
            ports = list(serial.tools.list_ports.comports())
            port_list = [port.device for port in ports]
            
            # Update port combo if it exists
            if hasattr(self.main_app, 'port_combo'):
                current_ports = list(self.main_app.port_combo.cget("values"))
                for port in port_list:
                    if port not in current_ports:
                        current_ports.append(port)
                self.main_app.port_combo.config(values=current_ports)
            
            if ports:
                print(f"Detected {len(ports)} port(s): {', '.join(port_list)}")
            else:
                print("No COM ports detected")
                
        except Exception as e:
            print(f"Port detection error: {e}")
    
    def auto_detect_devices(self):
        """Automatically detect connected devices"""
        try:
            ports = list(serial.tools.list_ports.comports())
            detected_devices = []
            
            for port in ports:
                try:
                    device_info = self.identify_device(port.device)
                    if device_info:
                        detected_devices.append(device_info)
                        self.device_status[port.device] = device_info
                except Exception as e:
                    continue
            
            # Update UI if possible
            if hasattr(self.main_app, 'update_device_status'):
                self.main_app.root.after(0, self.main_app.update_device_status, detected_devices)
            
        except Exception as e:
            print(f"Device detection error: {e}")
    
    def identify_device(self, port):
        """Identify device type on specific port"""
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(0.1)
            
            # Send identification commands
            ser.write(b'AT+RST\r\n')
            time.sleep(1)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                ser.close()
                
                if "ESP8266" in response or "ready" in response.lower():
                    return {"type": "ESP8266", "status": "Ready", "port": port}
                elif "ESP32" in response:
                    return {"type": "ESP32", "status": "Ready", "port": port}
                else:
                    return {"type": "Unknown", "status": "Connected", "port": port}
            
            ser.close()
            return None
            
        except Exception as e:
            return None
    
    def validate_firmware_enhanced(self, file_path, device_type):
        """Enhanced firmware validation"""
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            # File size check
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return False, "File is empty"
            
            # File type validation
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if device_type in ["ESP8266", "ESP32"]:
                if file_ext not in [".bin", ".hex", ".dat"]:
                    return False, f"Invalid file type for {device_type}"
            elif device_type == "AVR" and file_ext != ".hex":
                return False, "AVR requires .hex files"
            
            # Checksum calculation
            checksum = self.calculate_file_checksum(file_path)
            
            return True, f"Valid {file_ext.upper()} file ({file_size} bytes, MD5: {checksum[:8]}...)"
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def calculate_file_checksum(self, file_path):
        """Calculate MD5 checksum of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return "ERROR"
    
    def enhanced_upload_with_retry(self, upload_func, *args, **kwargs):
        """Enhanced upload with automatic retry logic"""
        self.upload_retry_count = 0
        self.upload_start_time = time.time()
        
        while self.upload_retry_count <= self.max_retries:
            try:
                result = upload_func(*args, **kwargs)
                if result:
                    return True
                else:
                    raise Exception("Upload failed")
                    
            except Exception as e:
                self.upload_retry_count += 1
                
                if self.upload_retry_count <= self.max_retries:
                    print(f"Upload error: {e}")
                    print(f"Retrying upload ({self.upload_retry_count}/{self.max_retries})...")
                    time.sleep(2)  # Wait before retry
                else:
                    print(f"Max retries exceeded. Upload failed.")
                    return False
        
        return False
    
    def test_connection_enhanced(self, port, baud_rate):
        """Enhanced connection testing"""
        try:
            ser = serial.Serial(port, int(baud_rate), timeout=2)
            if ser.is_open:
                print(f"Port {port} opened successfully")
                
                # Try to identify device
                device_info = self.identify_device(port)
                if device_info:
                    print(f"Device identified: {device_info['type']}")
                else:
                    print("Device type not identified")
                
                ser.close()
                return True
            else:
                print(f"Failed to open port {port}")
                return False
                
        except serial.SerialException as e:
            error_msg = str(e)
            if "Access is denied" in error_msg:
                print(f"Port {port} is in use by another application")
            elif "File not found" in error_msg:
                print(f"Port {port} not found")
            else:
                print(f"Connection error: {error_msg}")
            return False
    
    def create_upload_session(self, device, firmware, port, baud):
        """Create a new upload session for tracking"""
        return {
            "timestamp": datetime.now().isoformat(),
            "device": device,
            "firmware": os.path.basename(firmware),
            "port": port,
            "baud": baud,
            "status": "Starting",
            "start_time": time.time()
        }
    
    def update_upload_progress(self, progress, message, time_remaining=None, speed=None):
        """Update upload progress with enhanced information"""
        # This would be called by the main app to update progress
        print(f"Progress: {progress}% - {message}")
        if time_remaining:
            print(f"Time remaining: {time_remaining:.1f}s")
        if speed:
            print(f"Upload speed: {speed}")

# Example usage:
# enhanced = EnhancedFeatures(main_app)
# enhanced.start_auto_detection()
