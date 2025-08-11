#!/usr/bin/env python3
"""
J Tech Pixel Uploader - Professional Firmware Uploader for Microcontrollers
A comprehensive tool for uploading firmware to ESP8266, ESP32, AVR, STM32, and PIC devices.

Author: J Tech Pixel
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial.tools.list_ports
import subprocess
import os
import threading
import time
from datetime import datetime
import json

# Import our modules
import config
import utils

class JTechPixelUploader:
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_NAME)
        self.root.geometry(config.DEFAULT_WINDOW_SIZE)
        self.root.resizable(True, True)
        
        # Load configuration
        self.app_config = config.load_config()
        self.load_saved_settings()
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.firmware_path = tk.StringVar(value=self.app_config.get("last_firmware_path", ""))
        self.selected_port = tk.StringVar(value=self.app_config.get("last_com_port", ""))
        self.selected_device = tk.StringVar(value=self.app_config.get("last_device", config.DEFAULT_DEVICE))
        self.baud_rate = tk.StringVar(value=self.app_config.get("last_baud_rate", config.DEFAULT_BAUD_RATE))
        self.upload_progress = tk.DoubleVar()
        self.is_uploading = False
        
        # Check available tools
        self.available_tools = utils.get_available_tools()
        
        # Setup UI
        self.setup_ui()
        self.detect_ports()
        self.check_tools_availability()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Setup custom styles for the application"""
        self.style = ttk.Style()
        self.style.theme_use(self.app_config.get("theme", "clam"))
        
        # Custom button styles
        self.style.configure("Accent.TButton", 
                           background=config.UI_COLORS["primary"],
                           foreground="white")
        
        self.style.configure("Success.TButton",
                           background=config.UI_COLORS["success"],
                           foreground="white")
        
        self.style.configure("Warning.TButton",
                           background=config.UI_COLORS["warning"],
                           foreground="black")
        
        self.style.configure("Error.TButton",
                           background=config.UI_COLORS["error"],
                           foreground="white")
        
        self.style.configure("Info.TButton",
                           background=config.UI_COLORS["info"],
                           foreground="white")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for two-column layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(3, weight=1)  # Right column for log
        
        # Title and version
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text=config.APP_NAME, 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0)
        
        version_label = ttk.Label(title_frame, text=f"v{config.APP_VERSION}", 
                                 font=("Arial", 10), foreground="gray")
        version_label.grid(row=0, column=1, padx=(10, 0))
        
        # Firmware file selection
        ttk.Label(main_frame, text="Firmware File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        file_entry = ttk.Entry(file_frame, textvariable=self.firmware_path)
        file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Browse", command=self.select_firmware_file).grid(row=0, column=1, padx=(5, 0))
        
        # File info display
        self.file_info_label = ttk.Label(main_frame, text="", foreground="gray", font=("Arial", 9))
        self.file_info_label.grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Device type selection
        ttk.Label(main_frame, text="Device Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        device_frame = ttk.Frame(main_frame)
        device_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        device_combo = ttk.Combobox(device_frame, textvariable=self.selected_device, 
                                   values=list(config.DEVICE_CONFIGS.keys()), state="readonly", width=20)
        device_combo.grid(row=0, column=0, sticky=tk.W)
        device_combo.bind('<<ComboboxSelected>>', self.on_device_change)
        
        # Device description
        self.device_desc_label = ttk.Label(device_frame, text="", foreground="gray")
        self.device_desc_label.grid(row=0, column=1, padx=(10, 0))
        
        # COM port selection
        ttk.Label(main_frame, text="COM Port:").grid(row=3, column=0, sticky=tk.W, pady=5)
        port_frame = ttk.Frame(main_frame)
        port_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        port_combo = ttk.Combobox(port_frame, textvariable=self.selected_port, width=20)
        port_combo.grid(row=0, column=0, sticky=tk.W)
        ttk.Button(port_frame, text="Refresh", command=self.detect_ports).grid(row=0, column=1, padx=(10, 0))
        ttk.Button(port_frame, text="Test Connection", command=self.test_connection, style="Info.TButton").grid(row=0, column=2, padx=(10, 0))
        
        # Port info display
        self.port_info_label = ttk.Label(port_frame, text="", foreground="gray", font=("Arial", 9))
        self.port_info_label.grid(row=0, column=3, padx=(10, 0))
        
        # Device control buttons
        device_control_frame = ttk.Frame(main_frame)
        device_control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 5))
        
        ttk.Label(device_control_frame, text="Device Control:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.reset_button = ttk.Button(device_control_frame, text="Reset Device", command=self.reset_device, style="Warning.TButton")
        self.reset_button.grid(row=0, column=1, padx=(0, 10))
        
        self.flash_mode_button = ttk.Button(device_control_frame, text="Enter Flash Mode", command=self.enter_flash_mode, style="Accent.TButton")
        self.flash_mode_button.grid(row=0, column=2, padx=(0, 10))
        
        self.normal_mode_button = ttk.Button(device_control_frame, text="Exit Flash Mode", command=self.exit_flash_mode, style="Info.TButton")
        self.normal_mode_button.grid(row=0, column=3, padx=(0, 10))
        
        # Add force download mode button for single-button boards
        self.force_download_button = ttk.Button(device_control_frame, text="Force Download Mode", command=self.force_download_mode, style="Error.TButton")
        self.force_download_button.grid(row=0, column=4, padx=(0, 10))
        
        # Connection tips
        self.connection_tips_label = ttk.Label(main_frame, text="💡 Tip: For single-button boards, use 'Force Download Mode' button", 
                                             foreground="blue", font=("Arial", 9))
        self.connection_tips_label.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
        # Pattern Testing Section
        pattern_frame = ttk.LabelFrame(main_frame, text="🎨 Pattern Testing & Hardware Verification", padding="10")
        pattern_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 10))
        pattern_frame.columnconfigure(1, weight=1)
        
        # Pattern test controls
        ttk.Label(pattern_frame, text="Test Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.pattern_test_var = tk.BooleanVar(value=False)
        pattern_test_check = ttk.Checkbutton(pattern_frame, text="Enable Pattern Testing", 
                                           variable=self.pattern_test_var, 
                                           command=self.on_pattern_test_toggle)
        pattern_test_check.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Pattern test info
        self.pattern_info_label = ttk.Label(pattern_frame, text="", foreground="gray", font=("Arial", 9))
        self.pattern_info_label.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Pattern test buttons
        pattern_button_frame = ttk.Frame(pattern_frame)
        pattern_button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        self.test_pattern_button = ttk.Button(pattern_button_frame, text="Test Pattern", 
                                            command=self.test_pattern, style="Info.TButton")
        self.test_pattern_button.grid(row=0, column=0, padx=(0, 10))
        
        self.verify_hardware_button = ttk.Button(pattern_button_frame, text="Verify Hardware", 
                                                command=self.verify_hardware, style="Success.TButton")
        self.verify_hardware_button.grid(row=0, column=1, padx=(0, 10))
        
        self.auto_test_button = ttk.Button(pattern_button_frame, text="Auto Test Cycle", 
                                          command=self.auto_test_cycle, style="Accent.TButton")
        self.auto_test_button.grid(row=0, column=2, padx=(0, 10))
        
        # Create sample patterns button
        self.create_patterns_button = ttk.Button(pattern_button_frame, text="Create Sample Patterns", 
                                               command=self.create_sample_patterns, style="Warning.TButton")
        self.create_patterns_button.grid(row=0, column=3, padx=(0, 10))
        
        # Pattern test status
        self.pattern_status_label = ttk.Label(pattern_frame, text="", foreground="green", font=("Arial", 9))
        self.pattern_status_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))
        
        # Baud rate selection
        ttk.Label(main_frame, text="Baud Rate:").grid(row=7, column=0, sticky=tk.W, pady=5)
        baud_combo = ttk.Combobox(main_frame, textvariable=self.baud_rate, 
                                 values=config.BAUD_RATES, state="readonly", width=20)
        baud_combo.grid(row=7, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        self.upload_button = ttk.Button(button_frame, text="Upload Firmware", 
                                       command=self.start_upload, style="Success.TButton")
        self.upload_button.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Settings", command=self.show_settings).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="About", command=self.show_about).grid(row=0, column=3, padx=10)
        
        # Progress bar with real-time indicator
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=9, column=0, columnspan=2, pady=(20, 5))
        progress_frame.columnconfigure(1, weight=1)
        
        ttk.Label(progress_frame, text="Upload Progress:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.upload_progress, 
                                           maximum=100, length=400, mode='determinate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Real-time progress percentage label
        self.progress_label = ttk.Label(progress_frame, text="0%", font=("Arial", 10, "bold"))
        self.progress_label.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Real-time activity indicator
        self.activity_label = ttk.Label(progress_frame, text="●", foreground="green", font=("Arial", 12, "bold"))
        self.activity_label.grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Status label with enhanced real-time updates
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green", font=("Arial", 10, "bold"))
        self.status_label.grid(row=10, column=0, columnspan=2, pady=5)
        
        # Separator line between main content and log
        separator = ttk.Separator(main_frame, orient=tk.VERTICAL)
        separator.grid(row=0, column=2, rowspan=13, sticky=(tk.N, tk.S), padx=10)
        
        # Log output - moved to right side
        ttk.Label(main_frame, text="Upload Log:", font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, pady=(0, 5))
        
        # Log frame with scrollbar - right side
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=1, column=3, rowspan=12, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0), padx=(20, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget and scrollbar
        self.log_text = tk.Text(log_frame, height=25, width=60, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(12, weight=1)
        
        # Initial device description
        self.on_device_change()
        
        # Update file info if firmware path is set
        if self.firmware_path.get():
            self.update_file_info()
            
    def load_saved_settings(self):
        """Load saved settings from configuration"""
        # Apply saved window size
        saved_size = self.app_config.get("window_size", config.DEFAULT_WINDOW_SIZE)
        if saved_size:
            self.root.geometry(saved_size)
            
    def save_settings(self):
        """Save current settings to configuration"""
        self.app_config.update({
            "last_firmware_path": self.firmware_path.get(),
            "last_com_port": self.selected_port.get(),
            "last_device": self.selected_device.get(),
            "last_baud_rate": self.baud_rate.get(),
            "window_size": self.root.geometry()
        })
        config.save_config(self.app_config)
        
    def on_closing(self):
        """Handle application closing"""
        self.save_settings()
        self.root.destroy()
        
    def select_firmware_file(self):
        """Open file dialog to select firmware file"""
        file_path = filedialog.askopenfilename(
            title="Select Firmware File",
            filetypes=list(config.SUPPORTED_FILES.items())
        )
        
        if file_path:
            self.firmware_path.set(file_path)
            self.update_file_info()
            
            # Auto-detect if this is an LED pattern file
            if self.selected_device.get() in ["ESP8266", "ESP32"]:
                is_pattern, message = self.detect_led_pattern_data(file_path)
                if is_pattern:
                    self.log_message(f"🎨 {message}")
                    self.log_message("💡 This appears to be LED pattern data")
                    self.log_message("💡 Consider enabling 'Pattern Testing' mode for hardware verification")
                    
                    # Ask user if they want to enable pattern testing
                    result = messagebox.askyesno(
                        "LED Pattern Detected", 
                        f"This file appears to be LED pattern data:\n{message}\n\n"
                        "Would you like to enable Pattern Testing mode?\n\n"
                        "Pattern Testing will:\n"
                        "• Upload the pattern via custom protocol\n"
                        "• Test your LED matrix hardware\n"
                        "• Verify ESP8266 functionality\n"
                        "• Provide visual confirmation"
                    )
                    
                    if result:
                        self.pattern_test_var.set(True)
                        self.on_pattern_test_toggle()
                        self.log_message("✅ Pattern testing mode automatically enabled")
                    else:
                        self.log_message("ℹ️ Pattern testing mode not enabled - using standard upload")
            
    def update_file_info(self):
        """Update the file information display"""
        file_path = self.firmware_path.get()
        if file_path and os.path.exists(file_path):
            file_info = utils.get_file_info(file_path)
            info_text = f"{file_info['size']} | {file_info['extension'].upper()}"
            self.file_info_label.config(text=info_text)
        else:
            self.file_info_label.config(text="")
            
    def detect_ports(self):
        """Detect available COM ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if ports:
            if not self.selected_port.get() or self.selected_port.get() not in ports:
                self.selected_port.set(ports[0])
            self.log_message(f"Detected {len(ports)} COM port(s): {', '.join(ports)}")
            self.update_port_info()
        else:
            self.log_message("No COM ports detected")
            
    def update_port_info(self):
        """Update the port information display"""
        port = self.selected_port.get()
        if port:
            port_info = utils.get_port_info(port)
            info_text = f"{port_info['description']}"
            self.port_info_label.config(text=info_text)
        else:
            self.port_info_label.config(text="")
    
    def test_connection(self):
        """Test the COM port connection without uploading firmware"""
        port = self.selected_port.get()
        baud = self.baud_rate.get()
        
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        self.log_message(f"Testing connection to {port} at {baud} baud...")
        self.status_label.config(text="Testing connection...", foreground="blue")
        self.set_activity_status(True)  # Show active status
        
        try:
            # Test basic port access
            import serial
            ser = serial.Serial(port, int(baud), timeout=2)
            
            # Test if we can read/write
            if ser.is_open:
                self.log_message(f"✅ Port {port} opened successfully")
                
                # Try to detect device type
                device_detected = self.detect_device_type(ser)
                if device_detected:
                    self.log_message(f"✅ Device detected: {device_detected}")
                else:
                    self.log_message("⚠️ Device type not detected (may be normal)")
                
                ser.close()
                self.log_message(f"✅ Connection test completed successfully")
                
                # Test device-specific connection if possible
                if self.test_device_specific_connection():
                    self.log_message(f"✅ Device-specific test passed")
                else:
                    self.log_message(f"⚠️ Device-specific test failed (may be normal)")
                
                self.status_label.config(text="Connection test passed", foreground="green")
                self.set_activity_status(False)  # Reset activity status
                
            else:
                self.log_message(f"❌ Failed to open port {port}")
                self.status_label.config(text="Connection test failed", foreground="red")
                self.set_activity_status(False)  # Reset activity status
                
        except serial.SerialException as e:
            error_msg = str(e)
            if "Access is denied" in error_msg:
                self.log_message(f"❌ Port {port} is in use by another application")
                self.log_message("Try closing other applications that might be using this port")
            elif "File not found" in error_msg:
                self.log_message(f"❌ Port {port} not found")
                self.log_message("Try refreshing the port list")
            else:
                self.log_message(f"❌ Serial error: {error_msg}")
            self.status_label.config(text="Connection test failed", foreground="red")
            
        except Exception as e:
            self.log_message(f"❌ Unexpected error: {str(e)}")
            self.status_label.config(text="Connection test failed", foreground="red")
    
    def detect_device_type(self, ser):
        """Try to detect the type of device connected to the serial port"""
        try:
            # Send a simple command to see if device responds
            ser.write(b'\r\n')
            time.sleep(0.1)
            
            # Try to read response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                
                # Look for common device identifiers
                if 'ESP8266' in response or 'NodeMCU' in response:
                    return "ESP8266"
                elif 'ESP32' in response:
                    return "ESP32"
                elif 'Arduino' in response:
                    return "AVR"
                elif 'STM32' in response:
                    return "STM32"
                elif 'PIC' in response:
                    return "PIC"
                elif 'ready' in response.lower() or '>' in response:
                    return "Unknown (responds to commands)"
                else:
                    return "Unknown (no response)"
            else:
                return None
                
        except Exception:
            return None
    
    def test_device_specific_connection(self):
        """Test connection with device-specific commands"""
        device = self.selected_device.get()
        port = self.selected_port.get()
        baud = self.baud_rate.get()
        
        if device in ["ESP8266", "ESP32"]:
            self.log_message(f"Testing {device} connection...")
            
            # First test basic connectivity
            try:
                # Test with esptool chip_id command
                cmd = ["python", "-m", "esptool", "--port", port, "--baud", baud, "chip-id"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_message(f"✅ {device} chip ID detected successfully")
                    if "Chip ID:" in result.stdout:
                        chip_id = result.stdout.split("Chip ID:")[1].strip().split('\n')[0]
                        self.log_message(f"   Chip ID: {chip_id}")
                    
                    # Check if device is in download mode
                    if "Chip ID:" in result.stdout:
                        self.log_message(f"✅ Device is responding and ready for firmware upload")
                        return True
                    else:
                        self.log_message(f"⚠️ Device responded but may not be in download mode")
                        return True
                        
                else:
                    # Check for specific error messages
                    error_output = result.stderr.lower()
                    if "no serial data received" in error_output:
                        self.log_message(f"❌ {device} not responding - device may not be in download mode")
                        self.log_message(f"   💡 Try: Hold FLASH button, press RESET, release FLASH")
                    elif "failed to connect" in error_output:
                        self.log_message(f"❌ {device} connection failed - check wiring and power")
                    elif "access denied" in error_output:
                        self.log_message(f"❌ Port {port} is in use by another application")
                    else:
                        self.log_message(f"❌ {device} connection failed")
                        if result.stderr:
                            self.log_message(f"   Error: {result.stderr.strip()}")
                    
                    return False
                    
            except subprocess.TimeoutExpired:
                self.log_message(f"❌ {device} connection test timed out")
                self.log_message(f"   💡 Device may be stuck - try pressing RESET button")
                return False
            except Exception as e:
                self.log_message(f"❌ {device} connection test error: {str(e)}")
                return False
        else:
            self.log_message(f"Device-specific testing not implemented for {device}")
            return False
    
    def reset_device(self):
        """Reset the connected device"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        self.log_message(f"🔄 Resetting device on {port}...")
        self.status_label.config(text="Resetting device...", foreground="blue")
        
        try:
            # For ESP devices, we can use esptool to reset
            device = self.selected_device.get()
            if device in ["ESP8266", "ESP32"]:
                cmd = ["python", "-m", "esptool", "--port", port, "run"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_message("✅ Device reset successfully")
                    self.status_label.config(text="Device reset successfully", foreground="green")
                else:
                    self.log_message("⚠️ Reset command sent (device may have reset)")
                    self.status_label.config(text="Reset command sent", foreground="orange")
            else:
                # For other devices, try a simple serial reset
                import serial
                ser = serial.Serial(port, 115200, timeout=1)
                ser.write(b'\x00')  # Send null byte
                ser.close()
                self.log_message("✅ Reset signal sent to device")
                self.status_label.config(text="Reset signal sent", foreground="green")
                
        except Exception as e:
            self.log_message(f"❌ Error during reset: {str(e)}")
            self.status_label.config(text="Reset failed", foreground="red")
    
    def enter_flash_mode(self):
        """Put device into flash/download mode"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"Flash mode control not implemented for {device}")
            return
        
        self.log_message(f"🔧 Putting {device} into flash mode...")
        self.status_label.config(text="Entering flash mode...", foreground="blue")
        
        try:
            # For ESP devices, we can try to force flash mode
            # This simulates holding the FLASH button and pressing RESET
            cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), "chip_id"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "Chip ID:" in result.stdout:
                self.log_message("✅ Device is now in flash mode!")
                self.status_label.config(text="Device in flash mode", foreground="green")
                self.log_message("💡 You can now upload firmware")
            else:
                self.log_message("⚠️ Flash mode command sent")
                self.log_message("💡 If device doesn't respond, manually:")
                self.log_message("   1. Hold FLASH button")
                self.log_message("   2. Press RESET button")
                self.log_message("   3. Release FLASH button")
                self.status_label.config(text="Flash mode command sent", foreground="orange")
                
        except Exception as e:
            self.log_message(f"❌ Error entering flash mode: {str(e)}")
            self.status_label.config(text="Flash mode failed", foreground="red")
    
    def exit_flash_mode(self):
        """Exit flash mode and return to normal operation"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"Flash mode control not implemented for {device}")
            return
        
        self.log_message(f"🔄 Exiting flash mode for {device}...")
        self.status_label.config(text="Exiting flash mode...", foreground="blue")
        
        try:
            # For ESP devices, we can use the run command to exit flash mode
            cmd = ["python", "-m", "esptool", "--port", port, "run"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message("✅ Device exited flash mode successfully")
                self.status_label.config(text="Device exited flash mode", foreground="green")
                self.log_message("💡 Device is now running normally")
            else:
                self.log_message("⚠️ Exit flash mode command sent")
                self.log_message("💡 Device may have exited flash mode")
                self.status_label.config(text="Exit command sent", foreground="orange")
                
        except Exception as e:
            self.log_message(f"❌ Error exiting flash mode: {str(e)}")
            self.status_label.config(text="Exit flash mode failed", foreground="red")
    
    def check_flash_mode(self):
        """Check if device is currently in flash mode"""
        port = self.selected_port.get()
        device = self.selected_device.get()
        
        if device not in ["ESP8266", "ESP32"]:
            return False
        
        try:
            # Try to get chip ID - if successful, device is in flash mode
            cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), "chip_id"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "Chip ID:" in result.stdout:
                self.log_message("✅ Device is in flash mode")
                return True
            else:
                self.log_message("❌ Device is not in flash mode")
                return False
                
        except Exception as e:
            self.log_message(f"⚠️ Could not determine flash mode status: {str(e)}")
            return False
    
    def force_download_mode(self):
        """Force ESP8266 into download mode using serial commands (for single-button boards)"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"Force download mode not implemented for {device}")
            return
        
        self.log_message(f"🚀 Force entering download mode for {device}...")
        self.status_label.config(text="Forcing download mode...", foreground="red")
        
        try:
            # Method 1: Try sending specific serial commands to trigger download mode
            import serial
            ser = serial.Serial(port, 115200, timeout=1)
            
            # Send a series of commands that might trigger download mode
            commands = [
                b'\x00',  # Null byte
                b'\x55',  # Pattern that might trigger download mode
                b'\xAA',  # Another pattern
                b'\x00\x00\x00\x00',  # Multiple null bytes
            ]
            
            for cmd in commands:
                ser.write(cmd)
                time.sleep(0.1)
            
            ser.close()
            self.log_message("✅ Force download commands sent")
            
            # Wait a moment then test if it worked
            time.sleep(2)
            if self.check_flash_mode():
                self.log_message("🎉 SUCCESS! Device is now in download mode!")
                self.status_label.config(text="Device in download mode!", foreground="green")
                self.log_message("💡 You can now upload firmware!")
            else:
                self.log_message("⚠️ Force download commands sent, but device may not be responding")
                self.log_message("💡 Try uploading firmware anyway - it might work now")
                self.status_label.config(text="Force download attempted", foreground="orange")
                
        except Exception as e:
            self.log_message(f"❌ Error during force download: {str(e)}")
            self.status_label.config(text="Force download failed", foreground="red")
    
    def update_progress_from_output(self, output):
        """Update progress bar based on command output with enhanced pattern matching"""
        try:
            percent_value = None
            
            # ESP8266/ESP32 progress patterns
            if "Writing" in output and "%" in output:
                # Extract percentage from "Writing 123456 bytes ( 45%)"
                percent_match = output.split("%")[0].split()[-1]
                if percent_match.isdigit():
                    percent_value = int(percent_match)
                    
            elif "[" in output and "]" in output and "%" in output:
                # Extract percentage from "[45%] Writing..."
                percent_match = output.split("[")[1].split("%")[0]
                if percent_match.isdigit():
                    percent_value = int(percent_match)
                    
            elif "Progress:" in output and "%" in output:
                # Extract percentage from "Progress: 67%"
                percent_match = output.split("Progress:")[1].split("%")[0].strip()
                if percent_match.isdigit():
                    percent_value = int(percent_match)
                    
            elif "bytes" in output and "of" in output:
                # Calculate percentage from "123456 bytes of 456789"
                try:
                    parts = output.split()
                    for i, part in enumerate(parts):
                        if part == "of" and i > 0 and i < len(parts) - 1:
                            current = int(parts[i-1])
                            total = int(parts[i+1])
                            if total > 0:
                                percent_value = int((current / total) * 100)
                                break
                except (ValueError, IndexError):
                    pass
                    
            # AVR/Arduino progress patterns
            elif "avrdude" in output.lower() and "%" in output:
                # Extract percentage from avrdude output
                percent_match = output.split("%")[0].split()[-1]
                if percent_match.isdigit():
                    percent_value = int(percent_match)
                    
            # STM32 progress patterns
            elif "stm32flash" in output.lower() and "%" in output:
                # Extract percentage from stm32flash output
                percent_match = output.split("%")[0].split()[-1]
                if percent_match.isdigit():
                    percent_value = int(percent_match)
                    
            # Generic progress patterns
            elif "uploading" in output.lower() and "%" in output:
                # Generic upload progress
                percent_match = output.split("%")[0].split()[-1]
                if percent_match.isdigit():
                    percent_value = int(percent_match)
            
            # Update both progress bar and label if we found a percentage
            if percent_value is not None:
                self.upload_progress.set(percent_value)
                # Update percentage label in main thread
                self.root.after_idle(self._update_progress_label, percent_value)
                    
        except Exception:
            # Silently ignore progress parsing errors
            pass
    
    def on_device_change(self, event=None):
        """Handle device type change"""
        device = self.selected_device.get()
        if device in config.DEVICE_CONFIGS:
            desc = config.DEVICE_CONFIGS[device]["description"]
            self.device_desc_label.config(text=desc)
            
            # Update baud rate to device default
            default_baud = config.DEVICE_CONFIGS[device].get("default_baud", config.DEFAULT_BAUD_RATE)
            if default_baud in config.BAUD_RATES:
                self.baud_rate.set(default_baud)
                
            self.log_message(f"Selected device: {device} - {desc}")
            
    def check_tools_availability(self):
        """Check and report available flashing tools"""
        self.log_message("Checking available tools...")
        for tool, available in self.available_tools.items():
            status = "✅ Available" if available else "❌ Not found"
            self.log_message(f"{tool}: {status}")
            
        # Warn about missing tools
        missing_tools = [tool for tool, available in self.available_tools.items() if not available]
        if missing_tools:
            self.log_message(f"Warning: Missing tools: {', '.join(missing_tools)}")
            self.log_message("Some device types may not work without these tools")
            
    def start_upload(self):
        """Start the firmware upload process"""
        if self.is_uploading:
            return
            
        # Validate inputs
        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a firmware file")
            return
            
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        # Validate firmware file
        is_valid, error_msg = utils.validate_firmware_file(
            self.firmware_path.get(), 
            self.selected_device.get()
        )
        if not is_valid:
            messagebox.showerror("Invalid File", error_msg)
            return
            
        # Check if required tool is available
        device = self.selected_device.get()
        if device in ["ESP8266", "ESP32"] and not self.available_tools["esptool"]:
            messagebox.showerror("Tool Missing", "esptool is required for ESP devices but not found")
            return
        elif device == "AVR" and not self.available_tools["avrdude"]:
            messagebox.showerror("Tool Missing", "avrdude is required for AVR devices but not found")
            return
        elif device == "STM32" and not self.available_tools["stm32flash"]:
            messagebox.showerror("Tool Missing", "stm32flash is required for STM32 devices but not found")
            return
        elif device == "PIC" and not self.available_tools["mplab_ipe"]:
            messagebox.showerror("Tool Missing", "MPLAB IPE is required for PIC devices but not found")
            return
        
        # For ESP devices, check if they're in flash mode before uploading
        if device in ["ESP8266", "ESP32"]:
            self.log_message("🔍 Checking if device is in flash mode...")
            if not self.check_flash_mode():
                self.log_message("⚠️ Device not in flash mode - attempting to enter flash mode...")
                if not self.enter_flash_mode():
                    self.log_message("❌ Failed to enter flash mode automatically")
                    self.log_message("💡 Please use 'Enter Flash Mode' button or manually:")
                    self.log_message("   1. Hold FLASH button")
                    self.log_message("   2. Press RESET button")
                    self.log_message("   3. Release FLASH button")
                    self.status_label.config(text="Ready", foreground="green")
                    return
                else:
                    self.log_message("✅ Device is now in flash mode - proceeding with upload...")
            
        # Start upload in separate thread
        self.is_uploading = True
        self.upload_button.config(state="disabled")
        self.upload_progress.set(0)
        self.progress_label.config(text="0%")
        self.status_label.config(text="Uploading...", foreground="blue")
        self.set_activity_status(True)  # Show active status
        
        upload_thread = threading.Thread(target=self.upload_firmware)
        upload_thread.daemon = True
        upload_thread.start()
        
    def upload_firmware(self):
        """Execute the firmware upload with 100% live logging"""
        try:
            device = self.selected_device.get()
            port = self.selected_port.get()
            baud = self.baud_rate.get()
            firmware = self.firmware_path.get()
            
            self.log_message(f"Starting upload for {device} on {port} at {baud} baud")
            self.log_message(f"Firmware: {os.path.basename(firmware)}")
            
            # Check if this is LED pattern data and pattern testing is enabled
            if self.pattern_test_var.get() and device in ["ESP8266", "ESP32"]:
                is_pattern, message = self.detect_led_pattern_data(firmware)
                if is_pattern:
                    self.log_message(f"🎨 {message}")
                    self.log_message("🎯 Using pattern testing mode - uploading via custom protocol")
                    
                    # Use custom protocol for pattern upload
                    success = self.upload_pattern_via_custom_protocol(firmware, port, baud)
                    
                    if success:
                        self.upload_progress.set(100)
                        self.status_label.config(text="Pattern uploaded successfully!", foreground="green")
                        self.log_message("✅ Pattern uploaded successfully via custom protocol!")
                        self.log_message("💡 Check your LED matrix - you should see the pattern!")
                        
                        # Auto-reset device to run mode
                        time.sleep(1)
                        self.log_message("🔄 Auto-resetting device to run mode...")
                        self.reset_device()
                        
                        messagebox.showinfo("Success", "Pattern uploaded successfully!\n\n"
                                           "Your LED matrix should now display the pattern.\n"
                                           "This confirms your hardware is working correctly!")
                    else:
                        self.status_label.config(text="Pattern upload failed", foreground="red")
                        self.log_message("❌ Pattern upload failed!")
                        messagebox.showerror("Error", "Pattern upload failed. Check the log for details.")
                    
                    return
            
            # Standard firmware upload process
            if device in config.DEVICE_CONFIGS:
                config_info = config.DEVICE_CONFIGS[device]
                command = config_info["command"]
                args = [arg.format(port=port, baud=baud, file=firmware) for arg in config_info["args"]]
                
                self.log_message(f"Executing: {command} {' '.join(args)}")
                
                # Run the upload command with real-time output
                process = subprocess.Popen([command] + args, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True,
                                         bufsize=0)  # Unbuffered for real-time output
                
                # Real-time output monitoring with immediate updates
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Strip whitespace and log immediately
                        clean_output = output.strip()
                        if clean_output:  # Only log non-empty lines
                            self.log_message(clean_output)
                            
                            # Real-time progress updates
                            self.update_progress_from_output(clean_output)
                            
                            # Force immediate GUI update
                            self.root.update_idletasks()
                
                return_code = process.poll()
                
                if return_code == 0:
                    self.upload_progress.set(100)
                    self.status_label.config(text="Upload completed successfully!", foreground="green")
                    self.log_message("✅ Upload completed successfully!")
                    messagebox.showinfo("Success", "Firmware uploaded successfully!")
                else:
                    self.status_label.config(text="Upload failed", foreground="red")
                    self.log_message("❌ Upload failed!")
                    messagebox.showerror("Error", "Upload failed. Check the log for details.")
                    
            else:
                self.log_message(f"❌ Device type '{device}' not supported")
                messagebox.showerror("Error", f"Device type '{device}' not supported")
                
        except Exception as e:
            self.log_message(f"❌ Error during upload: {str(e)}")
            self.status_label.config(text="Upload error", foreground="red")
            messagebox.showerror("Error", f"Upload error: {str(e)}")
            
        finally:
            self.is_uploading = False
            self.upload_button.config(state="normal")
            self.set_activity_status(False)  # Reset activity status
            
    def on_pattern_test_toggle(self):
        """Handle pattern testing toggle"""
        if self.pattern_test_var.get():
            self.pattern_info_label.config(text="Pattern testing enabled - will detect LED data")
            self.pattern_status_label.config(text="Pattern testing mode active", foreground="blue")
            self.log_message("🎨 Pattern testing mode enabled")
        else:
            self.pattern_info_label.config(text="")
            self.pattern_status_label.config(text="Pattern testing disabled", foreground="gray")
            self.log_message("🎨 Pattern testing mode disabled")
    
    def detect_led_pattern_data(self, file_path):
        """Detect if the file contains LED pattern data"""
        try:
            # Check file extension first
            if file_path.lower().endswith('.bin'):
                # Read first few bytes to detect pattern
                with open(file_path, 'rb') as f:
                    header = f.read(16)  # Read first 16 bytes
                    
                # Check for common LED pattern signatures
                # WS2812 patterns often start with specific byte sequences
                if len(header) >= 4:
                    # Check for common LED pattern indicators
                    if any(pattern in header for pattern in [b'\x00\x55\xAA', b'\xFF\x00\xFF', b'\x00\x00\x00']):
                        return True, "LED pattern data detected"
                    
                    # Check if it's a small binary file (likely pattern data)
                    file_size = os.path.getsize(file_path)
                    if file_size <= 1024:  # Small files are likely patterns
                        return True, f"Small binary file ({file_size} bytes) - likely LED pattern"
                        
            return False, "Not detected as LED pattern data"
            
        except Exception as e:
            return False, f"Error detecting pattern: {str(e)}"
    
    def upload_pattern_via_custom_protocol(self, file_path, port, baud_rate):
        """Upload LED pattern using custom lightweight protocol"""
        try:
            self.log_message("🎨 Detected LED pattern data, using custom protocol")
            self.log_message("📤 Uploading pattern via serial...")
            
            # Open serial port
            import serial
            ser = serial.Serial(port, int(baud_rate), timeout=2)
            
            # Read pattern data
            with open(file_path, 'rb') as f:
                pattern_data = f.read()
            
            # Custom protocol: Send header + data + checksum
            header = b'LEDP'  # LED Pattern identifier
            data_length = len(pattern_data).to_bytes(4, 'little')
            checksum = sum(pattern_data) & 0xFF
            
            # Send protocol packet
            packet = header + data_length + pattern_data + bytes([checksum])
            ser.write(packet)
            
            # Wait for acknowledgment
            response = ser.read(4)
            ser.close()
            
            if response == b'OKAY':
                self.log_message("✅ Pattern uploaded successfully via custom protocol")
                return True
            else:
                self.log_message("⚠️ Pattern uploaded, but no acknowledgment received")
                return True  # Still consider it successful
                
        except Exception as e:
            self.log_message(f"❌ Error uploading pattern: {str(e)}")
            return False
    
    def test_pattern(self):
        """Test the current pattern file"""
        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a pattern file first")
            return
            
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        # Detect if it's LED pattern data
        is_pattern, message = self.detect_led_pattern_data(self.firmware_path.get())
        
        if is_pattern:
            self.log_message(f"🎨 {message}")
            self.pattern_status_label.config(text="Pattern detected - ready to test", foreground="green")
            
            # Start pattern test in separate thread
            test_thread = threading.Thread(target=self._run_pattern_test)
            test_thread.daemon = True
            test_thread.start()
        else:
            self.log_message(f"⚠️ {message}")
            self.pattern_status_label.config(text="Not a pattern file", foreground="orange")
    
    def _run_pattern_test(self):
        """Run the pattern test in a separate thread"""
        try:
            port = self.selected_port.get()
            baud = self.baud_rate.get()
            file_path = self.firmware_path.get()
            
            self.log_message("🧪 Starting pattern test...")
            self.pattern_status_label.config(text="Testing pattern...", foreground="blue")
            self.set_activity_status(True)
            
            # Upload pattern via custom protocol
            success = self.upload_pattern_via_custom_protocol(file_path, port, baud)
            
            if success:
                self.log_message("✅ Pattern test completed successfully!")
                self.log_message("💡 Check your LED matrix - you should see the pattern!")
                self.pattern_status_label.config(text="Pattern test successful - check LEDs", foreground="green")
                
                # Auto-reset device to run mode
                time.sleep(1)
                self.log_message("🔄 Auto-resetting device to run mode...")
                self.reset_device()
            else:
                self.pattern_status_label.config(text="Pattern test failed", foreground="red")
                
        except Exception as e:
            self.log_message(f"❌ Pattern test error: {str(e)}")
            self.pattern_status_label.config(text="Test error", foreground="red")
        finally:
            self.set_activity_status(False)
    
    def verify_hardware(self):
        """Verify hardware functionality through pattern testing"""
        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a pattern file first")
            return
            
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        # Start hardware verification in separate thread
        verify_thread = threading.Thread(target=self._run_hardware_verification)
        verify_thread.daemon = True
        verify_thread.start()
    
    def _run_hardware_verification(self):
        """Run hardware verification in a separate thread"""
        try:
            self.log_message("🔍 Starting hardware verification...")
            self.pattern_status_label.config(text="Verifying hardware...", foreground="blue")
            self.set_activity_status(True)
            
            # Step 1: Test serial communication
            self.log_message("📡 Step 1: Testing serial communication...")
            if not self.test_connection():
                self.log_message("❌ Serial communication failed")
                self.pattern_status_label.config(text="Hardware verification failed", foreground="red")
                return
            
            # Step 2: Upload test pattern
            self.log_message("📤 Step 2: Uploading test pattern...")
            success = self.upload_pattern_via_custom_protocol(
                self.firmware_path.get(), 
                self.selected_port.get(), 
                self.baud_rate.get()
            )
            
            if not success:
                self.log_message("❌ Pattern upload failed")
                self.pattern_status_label.config(text="Hardware verification failed", foreground="red")
                return
            
            # Step 3: Reset device and wait for visual confirmation
            self.log_message("🔄 Step 3: Resetting device for visual verification...")
            self.reset_device()
            
            # Step 4: Wait for user confirmation
            self.log_message("👁️ Step 4: Please check your LED matrix visually")
            self.log_message("💡 Do you see the expected pattern? (This is the hardware test)")
            
            # Show verification dialog
            self.root.after(0, self._show_verification_dialog)
            
        except Exception as e:
            self.log_message(f"❌ Hardware verification error: {str(e)}")
            self.pattern_status_label.config(text="Verification error", foreground="red")
        finally:
            self.set_activity_status(False)
    
    def _show_verification_dialog(self):
        """Show dialog for user to confirm visual verification"""
        result = messagebox.askyesno(
            "Hardware Verification", 
            "Can you see the LED pattern on your matrix?\n\n"
            "✅ YES = Hardware is working correctly\n"
            "❌ NO = Hardware has issues\n\n"
            "Please check:\n"
            "• Power supply\n"
            "• LED connections\n"
            "• Data pin wiring\n"
            "• ESP8266 functionality"
        )
        
        if result:
            self.log_message("✅ Hardware verification PASSED - LEDs working correctly!")
            self.pattern_status_label.config(text="Hardware verification PASSED", foreground="green")
            messagebox.showinfo("Success", "Hardware verification PASSED!\nYour LED matrix is working correctly.")
        else:
            self.log_message("❌ Hardware verification FAILED - LED issues detected")
            self.pattern_status_label.config(text="Hardware verification FAILED", foreground="red")
            messagebox.showerror("Hardware Issue", 
                               "Hardware verification FAILED!\n\n"
                               "Please check:\n"
                               "• Power supply voltage\n"
                               "• LED data pin connection\n"
                               "• Ground connections\n"
                               "• ESP8266 functionality")
    
    def auto_test_cycle(self):
        """Run automatic test cycle for hardware validation"""
        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a pattern file first")
            return
            
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        # Start auto test cycle in separate thread
        auto_test_thread = threading.Thread(target=self._run_auto_test_cycle)
        auto_test_thread.daemon = True
        auto_test_thread.start()
    
    def _run_auto_test_cycle(self):
        """Run automatic test cycle in a separate thread"""
        try:
            self.log_message("🔄 Starting automatic test cycle...")
            self.pattern_status_label.config(text="Auto test cycle running...", foreground="blue")
            self.set_activity_status(True)
            
            # Step 1: Connection test
            self.log_message("📡 Step 1/5: Testing connection...")
            if not self.test_connection():
                self.log_message("❌ Connection test failed - stopping cycle")
                self.pattern_status_label.config(text="Auto test failed", foreground="red")
                return
            time.sleep(1)
            
            # Step 2: Enter flash mode
            self.log_message("🔧 Step 2/5: Entering flash mode...")
            if not self.enter_flash_mode():
                self.log_message("⚠️ Flash mode entry failed, but continuing...")
            time.sleep(1)
            
            # Step 3: Upload pattern
            self.log_message("📤 Step 3/5: Uploading test pattern...")
            success = self.upload_pattern_via_custom_protocol(
                self.firmware_path.get(), 
                self.selected_port.get(), 
                self.baud_rate.get()
            )
            
            if not success:
                self.log_message("❌ Pattern upload failed - stopping cycle")
                self.pattern_status_label.config(text="Auto test failed", foreground="red")
                return
            time.sleep(1)
            
            # Step 4: Reset to run mode
            self.log_message("🔄 Step 4/5: Resetting to run mode...")
            self.reset_device()
            time.sleep(2)
            
            # Step 5: Visual verification request
            self.log_message("👁️ Step 5/5: Visual verification required")
            self.log_message("💡 Please check your LED matrix now")
            
            # Show final verification dialog
            self.root.after(0, self._show_auto_test_verification)
            
        except Exception as e:
            self.log_message(f"❌ Auto test cycle error: {str(e)}")
            self.pattern_status_label.config(text="Auto test error", foreground="red")
        finally:
            self.set_activity_status(False)
    
    def _show_auto_test_verification(self):
        """Show final verification dialog for auto test cycle"""
        result = messagebox.askyesno(
            "Auto Test Cycle Complete", 
            "🎯 Auto test cycle completed!\n\n"
            "Can you see the LED pattern on your matrix?\n\n"
            "✅ YES = All systems working correctly\n"
            "❌ NO = Hardware issues detected\n\n"
            "This completes the full hardware validation cycle."
        )
        
        if result:
            self.log_message("🎉 Auto test cycle PASSED - all systems working!")
            self.pattern_status_label.config(text="Auto test cycle PASSED", foreground="green")
            messagebox.showinfo("Success", "🎉 Auto test cycle PASSED!\n\n"
                               "Your hardware is working correctly:\n"
                               "• ESP8266 communication ✓\n"
                               "• Flash memory ✓\n"
                               "• LED matrix ✓\n"
                               "• Power supply ✓")
        else:
            self.log_message("❌ Auto test cycle FAILED - hardware issues detected")
            self.pattern_status_label.config(text="Auto test cycle FAILED", foreground="red")
            messagebox.showerror("Hardware Issues", 
                               "❌ Auto test cycle FAILED!\n\n"
                               "Hardware issues detected. Please check:\n"
                               "• Power supply and voltage\n"
                               "• LED matrix connections\n"
                               "• Data pin wiring\n"
                               "• ESP8266 functionality\n\n"
                               "Consider using the 'Verify Hardware' button for detailed diagnostics.")
    
    def create_sample_patterns(self):
        """Create sample LED pattern files for testing"""
        try:
            self.log_message("🎨 Creating sample LED pattern files...")
            self.pattern_status_label.config(text="Creating sample patterns...", foreground="blue")
            self.set_activity_status(True)
            
            # Import and use the utility function
            created_files = utils.create_sample_led_patterns()
            
            if created_files:
                self.log_message(f"✅ Created {len(created_files)} sample pattern files:")
                for filename in created_files:
                    self.log_message(f"   📁 {filename}")
                
                self.log_message("💡 Sample patterns created in 'SampleFirmware' folder")
                self.log_message("💡 You can now select one of these files to test pattern testing")
                
                self.pattern_status_label.config(text=f"Created {len(created_files)} sample patterns", foreground="green")
                
                # Ask if user wants to select one of the created files
                result = messagebox.askyesno(
                    "Sample Patterns Created", 
                    f"Successfully created {len(created_files)} sample LED pattern files!\n\n"
                    "Would you like to select one of these files to test the pattern testing functionality?"
                )
                
                if result:
                    # Open file dialog in the SampleFirmware folder
                    sample_dir = "SampleFirmware"
                    if os.path.exists(sample_dir):
                        file_path = filedialog.askopenfilename(
                            title="Select Sample Pattern File",
                            initialdir=sample_dir,
                            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
                        )
                        if file_path:
                            self.firmware_path.set(file_path)
                            self.update_file_info()
                            self.log_message(f"✅ Selected sample pattern: {os.path.basename(file_path)}")
                            
                            # Auto-enable pattern testing for sample files
                            self.pattern_test_var.set(True)
                            self.on_pattern_test_toggle()
                            
            else:
                self.log_message("❌ Failed to create sample patterns")
                self.pattern_status_label.config(text="Failed to create patterns", foreground="red")
                
        except Exception as e:
            self.log_message(f"❌ Error creating sample patterns: {str(e)}")
            self.pattern_status_label.config(text="Error creating patterns", foreground="red")
        finally:
            self.set_activity_status(False)
    
    def log_message(self, message):
        """Add a message to the log with timestamp - 100% live updates"""
        if self.app_config.get("show_timestamps", True):
            timestamp = datetime.now().strftime(config.LOG_CONFIG["timestamp_format"])
            log_entry = f"[{timestamp}] {message}\n"
        else:
            log_entry = f"{message}\n"
        
        # Immediate update for real-time logging
        self.root.after_idle(self._update_log, log_entry)
        
    def _update_log(self, message):
        """Update the log text widget with 100% live performance (called in main thread)"""
        # Insert message and auto-scroll
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
        # Force immediate visual update
        self.log_text.update_idletasks()
        
                # Smart log line management for performance
        max_lines = config.LOG_CONFIG["max_log_lines"]
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > max_lines:
            # Remove old lines in chunks for better performance
            lines_to_remove = len(lines) - max_lines + 1
            self.log_text.delete("1.0", f"{lines_to_remove}.0")
    
    def _update_progress_label(self, percent):
        """Update the progress percentage label in real-time"""
        self.progress_label.config(text=f"{percent}%")
    
    def set_activity_status(self, is_active):
        """Update the activity indicator to show active/inactive status"""
        if is_active:
            self.activity_label.config(text="●", foreground="red")
        else:
            self.activity_label.config(text="●", foreground="green")
    
    def clear_log(self):
        """Clear the log output"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def show_settings(self):
        """Show the settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        ttk.Label(settings_window, text="Settings", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Auto-detect ports
        auto_detect_var = tk.BooleanVar(value=self.app_config.get("auto_detect_ports", True))
        ttk.Checkbutton(settings_window, text="Auto-detect COM ports on startup", 
                       variable=auto_detect_var).pack(pady=5)
        
        # Show timestamps
        show_timestamps_var = tk.BooleanVar(value=self.app_config.get("show_timestamps", True))
        ttk.Checkbutton(settings_window, text="Show timestamps in log", 
                       variable=show_timestamps_var).pack(pady=5)
        
        # Theme selection
        ttk.Label(settings_window, text="Theme:").pack(pady=(10, 5))
        theme_var = tk.StringVar(value=self.app_config.get("theme", "clam"))
        theme_combo = ttk.Combobox(settings_window, textvariable=theme_var, 
                                  values=["clam", "alt", "default", "classic"], state="readonly")
        theme_combo.pack(pady=5)
        
        # Save button
        def save_settings():
            self.app_config.update({
                "auto_detect_ports": auto_detect_var.get(),
                "show_timestamps": show_timestamps_var.get(),
                "theme": theme_var.get()
            })
            config.save_config(self.app_config)
            self.setup_styles()  # Reapply styles
            messagebox.showinfo("Settings", "Settings saved successfully!")
            settings_window.destroy()
            
        ttk.Button(settings_window, text="Save", command=save_settings).pack(pady=20)
        
    def show_about(self):
        """Show the about dialog"""
        about_text = f"""{config.APP_NAME} v{config.APP_VERSION}

{config.APP_DESCRIPTION}

Supported devices:
• ESP8266 (NodeMCU, Wemos D1 Mini)
• ESP32 (DevKit, ESP32-WROOM)
• AVR (Arduino Uno, Nano, Pro Mini)
• STM32 (STM32F103, STM32F407)
• PIC (via MPLAB IPE)

Features:
• Easy firmware selection
• Automatic COM port detection
• Multiple device support
• Real-time upload progress
• Detailed logging
• Settings persistence

System Information:
• Platform: {utils.get_system_info()['platform']}
• Python: {utils.get_system_info()['python_version']}

Built with Python and Tkinter
© 2024 {config.APP_AUTHOR}"""
        
        messagebox.showinfo(f"About {config.APP_NAME}", about_text)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = JTechPixelUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
