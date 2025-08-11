#!/usr/bin/env python3
"""
Demo script for J Tech Pixel Uploader
This script demonstrates the application features in a demo mode.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

class DemoUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("J Tech Pixel Uploader - Demo Mode")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Demo variables
        self.firmware_path = tk.StringVar(value="demo_firmware.bin")
        self.selected_port = tk.StringVar(value="COM3 (Demo)")
        self.selected_device = tk.StringVar(value="ESP8266")
        self.baud_rate = tk.StringVar(value="115200")
        self.upload_progress = tk.DoubleVar()
        self.is_uploading = False
        
        # Demo device configs
        self.device_configs = {
            "ESP8266": "ESP8266 NodeMCU, Wemos D1 Mini",
            "ESP32": "ESP32 DevKit, ESP32-WROOM",
            "AVR": "Arduino Uno, Nano, Pro Mini",
            "STM32": "STM32F103, STM32F407",
            "PIC": "PIC microcontrollers via MPLAB IPE"
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the demo user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, column=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="J Tech Pixel Uploader - Demo Mode", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Demo notice
        notice_label = ttk.Label(main_frame, text="🎭 This is a demo version - no actual uploads will occur", 
                                font=("Arial", 10), foreground="orange")
        notice_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Firmware file selection
        ttk.Label(main_frame, text="Firmware File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        file_entry = ttk.Entry(main_frame, textvariable=self.firmware_path, width=50)
        file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="Browse (Demo)", command=self.demo_browse).grid(row=2, column=2, pady=5)
        
        # Device type selection
        ttk.Label(main_frame, text="Device Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        device_combo = ttk.Combobox(main_frame, textvariable=self.selected_device, 
                                   values=list(self.device_configs.keys()), state="readonly", width=20)
        device_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        device_combo.bind('<<ComboboxSelected>>', self.on_device_change)
        
        # Device description
        self.device_desc_label = ttk.Label(main_frame, text="", foreground="gray")
        self.device_desc_label.grid(row=3, column=2, padx=(10, 0), pady=5)
        
        # COM port selection
        ttk.Label(main_frame, text="COM Port:").grid(row=4, column=0, sticky=tk.W, pady=5)
        port_combo = ttk.Combobox(main_frame, textvariable=self.selected_port, 
                                 values=["COM1 (Demo)", "COM2 (Demo)", "COM3 (Demo)", "COM4 (Demo)"], width=20)
        port_combo.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        ttk.Button(main_frame, text="Refresh (Demo)", command=self.demo_refresh_ports).grid(row=4, column=2, padx=(10, 0), pady=5)
        
        # Baud rate selection
        ttk.Label(main_frame, text="Baud Rate:").grid(row=5, column=0, sticky=tk.W, pady=5)
        baud_combo = ttk.Combobox(main_frame, textvariable=self.baud_rate, 
                                 values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"], 
                                 state="readonly", width=20)
        baud_combo.grid(row=5, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.upload_button = ttk.Button(button_frame, text="Upload Firmware (Demo)", 
                                       command=self.start_demo_upload, style="Success.TButton")
        self.upload_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Demo Features", command=self.show_demo_features).grid(row=0, column=2, padx=10)
        
        # Progress bar
        ttk.Label(main_frame, text="Upload Progress:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.upload_progress, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=7, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(20, 5))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready for demo", foreground="green")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Log output
        ttk.Label(main_frame, text="Demo Log:").grid(row=9, column=0, sticky=tk.W, pady=(20, 5))
        
        # Log frame with scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget and scrollbar
        self.log_text = tk.Text(log_frame, height=15, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(10, weight=1)
        
        # Initial setup
        self.on_device_change()
        self.log_message("🎭 Demo mode activated - Welcome to J Tech Pixel Uploader!")
        self.log_message("This demo shows all the features without requiring actual hardware.")
        self.log_message("Try selecting different devices and clicking 'Upload Firmware (Demo)'")
        
    def demo_browse(self):
        """Demo file browser"""
        self.log_message("📁 Demo file browser activated")
        self.log_message("In the real app, this would open a file dialog")
        self.firmware_path.set("demo_firmware_v2.bin")
        self.log_message("Selected demo firmware: demo_firmware_v2.bin")
        
    def demo_refresh_ports(self):
        """Demo port refresh"""
        self.log_message("🔄 Demo port refresh activated")
        self.log_message("In the real app, this would detect actual COM ports")
        self.log_message("Demo ports: COM1 (Demo), COM2 (Demo), COM3 (Demo), COM4 (Demo)")
        
    def on_device_change(self):
        """Handle device type change"""
        device = self.selected_device.get()
        if device in self.device_configs:
            desc = self.device_configs[device]
            self.device_desc_label.config(text=desc)
            self.log_message(f"🔧 Selected device: {device} - {desc}")
            
    def start_demo_upload(self):
        """Start the demo upload process"""
        if self.is_uploading:
            return
            
        self.is_uploading = True
        self.upload_button.config(state="disabled")
        self.upload_progress.set(0)
        self.status_label.config(text="Demo uploading...", foreground="blue")
        
        # Start demo upload in separate thread
        upload_thread = threading.Thread(target=self.demo_upload_firmware)
        upload_thread.daemon = True
        upload_thread.start()
        
    def demo_upload_firmware(self):
        """Execute the demo firmware upload"""
        try:
            device = self.selected_device.get()
            port = self.selected_port.get()
            baud = self.baud_rate.get()
            firmware = self.firmware_path.get()
            
            self.log_message(f"🚀 Starting demo upload for {device} on {port} at {baud} baud")
            self.log_message(f"📄 Firmware: {firmware}")
            self.log_message("🎭 This is a simulation - no actual upload occurs")
            
            # Simulate upload process
            steps = [
                ("Connecting to device...", 10),
                ("Entering bootloader mode...", 20),
                ("Verifying device...", 30),
                ("Erasing flash...", 50),
                ("Writing firmware...", 70),
                ("Verifying upload...", 90),
                ("Upload complete!", 100)
            ]
            
            for step, progress in steps:
                time.sleep(0.8)  # Simulate processing time
                self.log_message(f"⏳ {step}")
                self.upload_progress.set(progress)
                
            self.status_label.config(text="Demo upload completed successfully!", foreground="green")
            self.log_message("✅ Demo upload completed successfully!")
            self.log_message("🎉 In the real app, your firmware would now be uploaded!")
            
            messagebox.showinfo("Demo Success", "Demo upload completed successfully!\n\nThis was a simulation - no actual firmware was uploaded.")
            
        except Exception as e:
            self.log_message(f"❌ Demo upload error: {str(e)}")
            self.status_label.config(text="Demo upload error", foreground="red")
            
        finally:
            self.is_uploading = False
            self.upload_button.config(state="normal")
            
    def log_message(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Update log in main thread
        self.root.after(0, self._update_log, log_entry)
        
    def _update_log(self, message):
        """Update the log text widget"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear the log output"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🧹 Log cleared")
        
    def show_demo_features(self):
        """Show demo features information"""
        features_text = """🎭 Demo Features Available:

• Device Selection: Try different microcontroller types
• Port Simulation: Simulated COM port detection
• File Browser: Demo file selection
• Upload Simulation: Realistic upload process simulation
• Progress Tracking: Live progress bar updates
• Logging: Comprehensive demo logging
• Settings: Simulated configuration options

🔧 Real App Features:
• Actual firmware uploads to real devices
• Real COM port detection
• Hardware validation
• Error handling for real scenarios
• Settings persistence
• Cross-platform compatibility

Try clicking 'Upload Firmware (Demo)' to see the upload simulation!"""
        
        messagebox.showinfo("Demo Features", features_text)

def main():
    """Main demo entry point"""
    root = tk.Tk()
    app = DemoUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
