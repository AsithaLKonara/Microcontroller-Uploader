#!/usr/bin/env python3
"""
Test script for upload logging functionality
This script demonstrates how upload logs are automatically saved
"""

import os
import time
from datetime import datetime

def create_sample_upload_log():
    """Create a sample upload log to demonstrate the feature"""
    print("🧪 Testing Upload Logging System...")
    print("=" * 50)
    
    # Create upload logs directory
    upload_log_directory = "UploadLogs"
    os.makedirs(upload_log_directory, exist_ok=True)
    
    # Create a sample upload session
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    device = "ESP8266"
    firmware_name = "test_firmware"
    
    sample_session = {
        "timestamp": timestamp,
        "device": device,
        "firmware": firmware_name,
        "port": "COM3",
        "baud": "115200",
        "log_file": f"{upload_log_directory}/upload_{timestamp}_{device}_{firmware_name}.log",
        "start_time": time.time()
    }
    
    # Create sample log entries
    sample_logs = [
        {"timestamp": "10:00:01", "type": "INFO", "message": "📝 Upload session started: " + timestamp},
        {"timestamp": "10:00:01", "type": "INFO", "message": "📱 Device: ESP8266"},
        {"timestamp": "10:00:01", "type": "INFO", "message": "📁 Firmware: test_firmware"},
        {"timestamp": "10:00:01", "type": "INFO", "message": "🔌 Port: COM3"},
        {"timestamp": "10:00:01", "type": "INFO", "message": "⚡ Baud Rate: 115200"},
        {"timestamp": "10:00:01", "type": "INFO", "message": "=" * 50},
        {"timestamp": "10:00:02", "type": "INFO", "message": "Starting upload for ESP8266 on COM3 at 115200 baud"},
        {"timestamp": "10:00:02", "type": "INFO", "message": "Firmware: test_firmware.bin"},
        {"timestamp": "10:00:03", "type": "OUTPUT", "message": "esptool.py v4.7.0"},
        {"timestamp": "10:00:03", "type": "OUTPUT", "message": "Serial port COM3"},
        {"timestamp": "10:00:04", "type": "OUTPUT", "message": "Connecting..."},
        {"timestamp": "10:00:05", "type": "OUTPUT", "message": "Chip is ESP8266EX"},
        {"timestamp": "10:00:06", "type": "OUTPUT", "message": "Features: WiFi"},
        {"timestamp": "10:00:07", "type": "OUTPUT", "message": "Uploading stub..."},
        {"timestamp": "10:00:08", "type": "OUTPUT", "message": "Running stub..."},
        {"timestamp": "10:00:09", "type": "OUTPUT", "message": "Stub running..."},
        {"timestamp": "10:00:10", "type": "OUTPUT", "message": "Configuring flash size..."},
        {"timestamp": "10:00:11", "type": "OUTPUT", "message": "Flash will be erased from 0x00000 to 0x05fff..."},
        {"timestamp": "10:00:12", "type": "OUTPUT", "message": "Compressed 24576 bytes to 17823..."},
        {"timestamp": "10:00:13", "type": "OUTPUT", "message": "Writing 24576 bytes (17823 compressed) at 0x00000000 in 1.6 seconds (121.6 kbit/s)..."},
        {"timestamp": "10:00:15", "type": "OUTPUT", "message": "Hash of data verified."},
        {"timestamp": "10:00:16", "type": "OUTPUT", "message": "Leaving..."},
        {"timestamp": "10:00:17", "type": "OUTPUT", "message": "Hard resetting via RTS pin..."},
        {"timestamp": "10:00:18", "type": "SUCCESS", "message": "🎉 Upload completed successfully!"},
        {"timestamp": "10:00:18", "type": "INFO", "message": "💡 Your ESP8266 should now be running the new firmware!"}
    ]
    
    # Write the log file
    log_file = sample_session["log_file"]
    with open(log_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"J Tech Pixel Uploader - Upload Log\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Device: {sample_session['device']}\n")
        f.write(f"Firmware: {sample_session['firmware']}\n")
        f.write(f"Port: {sample_session['port']}\n")
        f.write(f"Baud Rate: {sample_session['baud']}\n")
        f.write(f"Duration: {time.time() - sample_session['start_time']:.2f} seconds\n")
        f.write("=" * 60 + "\n\n")
        
        # Write log entries
        for log_entry in sample_logs:
            f.write(f"[{log_entry['timestamp']}] {log_entry['type']}: {log_entry['message']}\n")
        
        # Write summary
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Upload completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total log entries: {len(sample_logs)}\n")
        f.write(f"Log file: {os.path.basename(log_file)}\n")
    
    print(f"✅ Sample upload log created: {os.path.basename(log_file)}")
    print(f"📁 Location: {upload_log_directory}/")
    
    # List all log files
    print(f"\n📋 Available upload logs:")
    if os.path.exists(upload_log_directory):
        log_files = [f for f in os.listdir(upload_log_directory) if f.endswith('.log')]
        if log_files:
            for log_file in sorted(log_files, reverse=True):
                filepath = os.path.join(upload_log_directory, log_file)
                stat = os.stat(filepath)
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"   📄 {log_file} ({size} bytes, {modified})")
        else:
            print("   No log files found")
    
    print(f"\n💡 Upload Logging Features:")
    print("   ✅ Automatic log creation on every upload")
    print("   ✅ Detailed session information")
    print("   ✅ Real-time command output capture")
    print("   ✅ Success/error status tracking")
    print("   ✅ Timestamped entries")
    print("   ✅ Easy log viewing and management")
    print("   ✅ Organized by device and firmware")
    
    print(f"\n🎯 To test in the main application:")
    print("   1. Run: python j_tech_pixel_uploader.py")
    print("   2. Click 'Upload Logs' button")
    print("   3. View available log files")
    print("   4. Double-click to view log contents")
    print("   5. Upload logs are created automatically!")

if __name__ == "__main__":
    create_sample_upload_log()
