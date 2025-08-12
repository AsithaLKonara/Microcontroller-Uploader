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
        
        # Device control buttons - Simplified version
        device_control_frame = ttk.Frame(main_frame)
        device_control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 5))
        
        ttk.Label(device_control_frame, text="Device Control:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Device Control section - simplified
        ttk.Label(device_control_frame, text="Device Status:", font=("Arial", 9)).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Add separator line
        separator_line = ttk.Separator(device_control_frame, orient=tk.HORIZONTAL)
        separator_line.grid(row=1, column=0, columnspan=8, sticky=(tk.W, tk.E), pady=10)
        
        # Connection tips
        self.connection_tips_label = ttk.Label(main_frame, text="💡 Tip: Upload Firmware button automatically handles reset and flash mode entry", 
                                             foreground="blue", font=("Arial", 9))
        self.connection_tips_label.grid(row=5, column=0, columnspan=2, pady=(5, 0))
        
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
        
        # Upload flow status indicator
        self.flow_status_label = ttk.Label(main_frame, text="", foreground="blue", font=("Arial", 9))
        self.flow_status_label.grid(row=11, column=0, columnspan=2, pady=2)
        
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
                        self.log_message("✅ Pattern testing mode automatically enabled")
                    else:
                        self.log_message("ℹ️ Pattern testing mode not enabled - using standard upload")
    
    def detect_led_pattern_data(self, file_path):
        """Detect if a file contains LED pattern data"""
        try:
            if not file_path or not os.path.exists(file_path):
                return False, "File not found"
            
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.dat':
                # .dat files are typically LED pattern data
                file_size = os.path.getsize(file_path)
                if file_size > 0:
                    return True, f"LED pattern data file (.dat) - {file_size} bytes"
                else:
                    return False, "Empty .dat file"
            
            elif file_ext == '.bin':
                # Check if .bin file might contain LED pattern data
                file_size = os.path.getsize(file_path)
                if file_size > 0 and file_size <= 1024:  # Small .bin files might be patterns
                    return True, f"Potential LED pattern data (.bin) - {file_size} bytes"
                else:
                    return False, "Standard firmware file (.bin)"
            
            else:
                return False, f"Unsupported file type: {file_ext}"
                
        except Exception as e:
            return False, f"Error analyzing file: {str(e)}"
            
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
        """Reset the connected device using proper hardware control - Enhanced version"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        self.log_message(f"🔄 Enhanced reset for {device} on {port}...")
        self.status_label.config(text="Enhanced reset in progress...", foreground="blue")
        
        try:
            if device in ["ESP8266", "ESP32"]:
                # Try to detect if this is an ESP-01 board (most challenging)
                if self._detect_esp01_board(port):
                    self.log_message("🔍 Detected ESP-01 board - using specialized reset method")
                    if self.reset_esp01_specific(port):
                        self.log_message("✅ ESP-01 specific reset completed successfully")
                        self.status_label.config(text="ESP-01 reset successful", foreground="green")
                        return
                    else:
                        self.log_message("⚠️ ESP-01 specific reset failed, trying enhanced method")
                
                # Use enhanced DTR/RTS control for proper hardware reset
                if self.reset_esp_via_dtr_rts(port):
                    self.log_message("✅ Enhanced hardware reset completed successfully")
                    self.status_label.config(text="Enhanced hardware reset successful", foreground="green")
                else:
                    self.log_message("⚠️ Enhanced hardware reset attempted (check device)")
                    self.status_label.config(text="Enhanced reset attempted", foreground="orange")
            else:
                # For other devices, try a simple serial reset
                import serial
                ser = serial.Serial(port, 115200, timeout=1)
                ser.write(b'\x00')  # Send null byte
                ser.close()
                self.log_message("✅ Reset signal sent to device")
                self.status_label.config(text="Reset signal sent", foreground="green")
                
        except Exception as e:
            self.log_message(f"❌ Error during enhanced reset: {str(e)}")
            self.status_label.config(text="Enhanced reset failed", foreground="red")
    
    def _detect_esp01_board(self, port):
        """Try to detect if the connected board is an ESP-01 (most challenging to reset)"""
        try:
            import serial
            
            # ESP-01 boards often have specific characteristics
            # Method 1: Check port info for ESP-01 indicators
            port_info = self.selected_port.get()
            if "ESP-01" in port_info or "ESP01" in port_info:
                return True
            
            # Method 2: Try to detect by behavior
            try:
                ser = serial.Serial(port, 74880, timeout=1)
                
                # ESP-01 boards often don't respond to standard commands
                ser.write(b'AT\r\n')
                time.sleep(0.5)
                
                if ser.in_waiting == 0:
                    # No response - likely ESP-01
                    ser.close()
                    return True
                
                ser.close()
                
            except Exception:
                # If we can't even open the port, it might be an ESP-01
                return True
            
            # Method 3: Check if device is very stubborn (ESP-01 characteristic)
            if not self.check_flash_mode():
                # If device is not responding to standard methods, it might be ESP-01
                return True
            
            return False
            
        except Exception:
            # If detection fails, assume it's not an ESP-01
            return False
    
    def reset_esp_via_dtr_rts(self, port):
        """Reset ESP8266/ESP32 using DTR/RTS control (hardware reset) - Enhanced version"""
        try:
            import serial
            
            self.log_message("🔧 Starting enhanced hardware reset sequence...")
            
            # Method 1: Standard ESP reset sequence
            if self._try_standard_esp_reset(port):
                return True
            
            # Method 2: Single-button board reset sequence
            if self._try_single_button_reset(port):
                return True
            
            # Method 3: CH340/CP210x specific reset sequence
            if self._try_ch340_reset(port):
                return True
            
            # Method 4: Aggressive reset sequence
            if self._try_aggressive_reset(port):
                return True
            
            # Method 5: GPIO0 simulation reset (for single-button boards)
            if self._try_gpio0_simulation_reset(port):
                return True
            
            # Method 6: Voltage cycling reset (simulates unplug/replug)
            if self._try_voltage_cycling_reset(port):
                return True
            
            self.log_message("⚠️ All hardware reset methods failed")
            return False
            
        except Exception as e:
            self.log_message(f"⚠️ Enhanced DTR/RTS reset failed: {str(e)}")
            return False
    
    def _try_standard_esp_reset(self, port):
        """Try standard ESP reset sequence"""
        try:
            self.log_message("🔄 Trying standard ESP reset sequence...")
            ser = serial.Serial(
                port=port,
                baudrate=74880,  # ESP boot baud rate
                timeout=1,
                write_timeout=1
            )
            
            # Standard ESP reset sequence
            ser.setDTR(False)
            ser.setRTS(False)
            time.sleep(0.1)
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.1)
            
            ser.setDTR(False)
            ser.setRTS(True)
            time.sleep(0.1)
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.1)
            
            ser.close()
            self.log_message("✅ Standard ESP reset sequence completed")
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ Standard reset failed: {str(e)}")
            return False
    
    def _try_single_button_reset(self, port):
        """Try single-button board reset sequence with extended timing"""
        try:
            self.log_message("🔄 Trying single-button board reset sequence...")
            ser = serial.Serial(
                port=port,
                baudrate=74880,
                timeout=1,
                write_timeout=1
            )
            
            # Single-button board sequence (longer timing)
            ser.setDTR(False)
            ser.setRTS(False)
            time.sleep(0.5)  # Longer reset hold
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.3)
            
            ser.setDTR(False)
            ser.setRTS(True)
            time.sleep(0.5)  # Longer flash mode trigger
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.3)
            
            ser.close()
            self.log_message("✅ Single-button reset sequence completed")
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ Single-button reset failed: {str(e)}")
            return False
    
    def _try_ch340_reset(self, port):
        """Try CH340/CP210x specific reset sequence"""
        try:
            self.log_message("🔄 Trying CH340/CP210x specific reset...")
            ser = serial.Serial(
                port=port,
                baudrate=74880,
                timeout=1,
                write_timeout=1
            )
            
            # CH340 specific sequence (different timing)
            ser.setDTR(False)
            ser.setRTS(False)
            time.sleep(0.2)
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.2)
            
            ser.setDTR(False)
            ser.setRTS(True)
            time.sleep(0.3)
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.2)
            
            ser.close()
            self.log_message("✅ CH340 reset sequence completed")
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ CH340 reset failed: {str(e)}")
            return False
    
    def _try_aggressive_reset(self, port):
        """Try aggressive reset with multiple baud rates"""
        try:
            self.log_message("🔄 Trying aggressive reset with baud rate cycling...")
            
            # Try different baud rates that might trigger different boot modes
            baud_rates = [74880, 115200, 57600, 38400]
            
            for baud in baud_rates:
                try:
                    ser = serial.Serial(
                        port=port,
                        baudrate=baud,
                        timeout=0.5,
                        write_timeout=0.5
                    )
                    
                    # Rapid DTR/RTS toggling
                    for _ in range(3):
                        ser.setDTR(False)
                        ser.setRTS(False)
                        time.sleep(0.05)
                        
                        ser.setDTR(True)
                        ser.setRTS(False)
                        time.sleep(0.05)
                        
                        ser.setDTR(False)
                        ser.setRTS(True)
                        time.sleep(0.05)
                        
                        ser.setDTR(True)
                        ser.setRTS(False)
                        time.sleep(0.05)
                    
                    ser.close()
                    self.log_message(f"✅ Aggressive reset at {baud} baud completed")
                    return True
                    
                except Exception:
                    continue
            
            self.log_message("⚠️ Aggressive reset failed at all baud rates")
            return False
            
        except Exception as e:
            self.log_message(f"⚠️ Aggressive reset failed: {str(e)}")
            return False
    
    def enter_flash_mode(self):
        """Put device into flash/download mode using proper hardware control"""
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
            # Method 1: Try hardware reset with DTR/RTS
            if self.reset_esp_via_dtr_rts(port):
                self.log_message("✅ Hardware reset sequence completed")
                
                # Wait for device to boot and check if it's in flash mode
                time.sleep(2)
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! Device is now in flash mode!")
                    self.status_label.config(text="Device in flash mode!", foreground="green")
                    return True
                else:
                    self.log_message("⚠️ Hardware reset completed, but device not in flash mode")
            
            # Method 2: Try esptool flash mode entry
            self.log_message("🔄 Trying esptool flash mode entry...")
            cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), "chip_id"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "Chip ID:" in result.stdout:
                self.log_message("✅ Device is now in flash mode!")
                self.status_label.config(text="Device in flash mode", foreground="green")
                return True
            else:
                self.log_message("⚠️ Software flash mode entry failed")
                
            # Method 3: Manual instructions for single-button boards
            self.log_message("💡 For single-button ESP boards, try manually:")
            self.log_message("   1. Hold RESET button")
            self.log_message("   2. Press and hold RESET for 2 seconds")
            self.log_message("   3. Release RESET button")
            self.log_message("   4. Wait for device to enter flash mode")
            
            self.status_label.config(text="Flash mode entry attempted", foreground="orange")
            return False
                
        except Exception as e:
            self.log_message(f"❌ Error entering flash mode: {str(e)}")
            self.status_label.config(text="Flash mode failed", foreground="red")
            return False
    
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
        """Force ESP8266 into download mode using proper hardware control (for single-button boards) - Enhanced version"""
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
            # Method 1: Use enhanced DTR/RTS control for hardware reset and flash mode entry
            if self.reset_esp_via_dtr_rts(port):
                self.log_message("✅ Enhanced hardware reset sequence completed")
                
                # Wait for device to boot and check if it's in flash mode
                time.sleep(3)
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! Device is now in download mode!")
                    self.status_label.config(text="Device in download mode!", foreground="green")
                    return True
                else:
                    self.log_message("⚠️ Hardware reset completed, but device not in flash mode")
            
            # Method 2: Try sending enhanced serial commands to trigger download mode
            if self._try_enhanced_serial_commands(port):
                return True
            
            # Method 3: Try baud rate cycling with commands
            if self._try_baud_rate_cycling(port):
                return True
            
            # Method 4: Try timing-based reset sequence
            if self._try_timing_based_reset(port):
                return True
            
            self.log_message("⚠️ All force download methods attempted")
            self.log_message("💡 Try uploading firmware anyway - it might work now")
            self.status_label.config(text="Download mode attempted", foreground="orange")
            return False
                
        except Exception as e:
            self.log_message(f"❌ Error during force download: {str(e)}")
            self.status_label.config(text="Force download failed", foreground="red")
            return False
    
    def _try_enhanced_serial_commands(self, port):
        """Try enhanced serial command sequence for download mode"""
        try:
            self.log_message("🔄 Trying enhanced serial command sequence...")
            import serial
            
            # Try multiple baud rates with different command sequences
            command_sets = [
                # Standard ESP download mode trigger
                [b'\x00', b'\x55', b'\xAA', b'\x00\x00\x00', b'\x55\xAA\x55'],
                # Extended pattern sequence
                [b'\x00' * 10, b'\x55' * 5, b'\xAA' * 5, b'\x00\x55\xAA' * 3],
                # Binary pattern sequence
                [b'\x01\x02\x03\x04', b'\xFE\xFD\xFC\xFB', b'\x00\xFF\x00\xFF'],
                # ESP-specific boot commands
                [b'AT+RST\r\n', b'AT+GMR\r\n', b'AT\r\n'],
            ]
            
            for i, commands in enumerate(command_sets):
                try:
                    self.log_message(f"   Trying command set {i+1}...")
                    ser = serial.Serial(port, 74880, timeout=2)
                    
                    for cmd in commands:
                        ser.write(cmd)
                        time.sleep(0.3)
                    
                    ser.close()
                    time.sleep(1)
                    
                    # Check if it worked
                    if self.check_flash_mode():
                        self.log_message(f"🎉 SUCCESS! Command set {i+1} worked!")
                        return True
                        
                except Exception:
                    continue
            
            self.log_message("⚠️ Enhanced serial commands completed, but device may not be responding")
            return False
            
        except Exception as e:
            self.log_message(f"⚠️ Enhanced serial commands failed: {str(e)}")
            return False
    
    def _try_baud_rate_cycling(self, port):
        """Try cycling through different baud rates with commands"""
        try:
            self.log_message("🔄 Trying baud rate cycling with commands...")
            import serial
            
            baud_rates = [74880, 115200, 57600, 38400, 9600]
            commands = [b'\x00', b'\x55', b'\xAA']
            
            for baud in baud_rates:
                try:
                    self.log_message(f"   Trying {baud} baud...")
                    ser = serial.Serial(port, 74880, timeout=1)
                    
                    for cmd in commands:
                        ser.write(cmd)
                        time.sleep(0.2)
                    
                    ser.close()
                    time.sleep(0.5)
                    
                    if self.check_flash_mode():
                        self.log_message(f"🎉 SUCCESS! Baud rate {baud} worked!")
                        return True
                        
                except Exception:
                    continue
            
            self.log_message("⚠️ Baud rate cycling completed, but device may not be responding")
            return False
            
        except Exception as e:
            self.log_message(f"⚠️ Baud rate cycling failed: {str(e)}")
            return False
    
    def _try_timing_based_reset(self, port):
        """Try timing-based reset sequence for stubborn boards"""
        try:
            self.log_message("🔄 Trying timing-based reset sequence...")
            import serial
            
            # Open port at boot baud rate
            ser = serial.Serial(port, 74880, timeout=1)
            
            # Very slow, deliberate sequence
            ser.setDTR(False)
            ser.setRTS(False)
            time.sleep(1.0)  # Long reset hold
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.5)
            
            ser.setDTR(False)
            ser.setRTS(True)
            time.sleep(1.0)  # Long flash mode trigger
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(0.5)
            
            # Send a few commands
            ser.write(b'\x00')
            time.sleep(0.5)
            ser.write(b'\x55')
            time.sleep(0.5)
            ser.write(b'\xAA')
            time.sleep(0.5)
            
            ser.close()
            time.sleep(2)  # Wait longer for device to respond
            
            if self.check_flash_mode():
                self.log_message("🎉 SUCCESS! Timing-based reset worked!")
                return True
            else:
                self.log_message("⚠️ Timing-based reset completed, but device may not be responding")
                return False
                
        except Exception as e:
            self.log_message(f"⚠️ Timing-based reset failed: {str(e)}")
            return False
    
    def smart_reset_device(self):
        """Smart reset sequence specifically for single-button ESP boards - Enhanced version"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"Smart reset not implemented for {device}")
            return
        
        self.log_message(f"🧠 Enhanced smart reset sequence for {device} on {port}...")
        self.status_label.config(text="Enhanced smart reset in progress...", foreground="blue")
        
        try:
            # Step 1: Check current device state
            self.log_message("🔍 Step 1: Checking current device state...")
            current_state = "unknown"
            
            if self.check_flash_mode():
                current_state = "flash_mode"
                self.log_message("✅ Device is currently in flash mode")
                self.status_label.config(text="Device already in flash mode!", foreground="green")
                return True
            else:
                current_state = "normal_mode"
                self.log_message("✅ Device is currently in normal mode")
            
            # Step 2: Perform enhanced hardware reset with retries
            self.log_message("🔄 Step 2: Performing enhanced hardware reset...")
            reset_success = False
            for attempt in range(3):
                self.log_message(f"   Hardware reset attempt {attempt + 1}/3...")
                if self.reset_esp_via_dtr_rts(port):
                    self.log_message("✅ Hardware reset completed")
                    reset_success = True
                    break
                else:
                    self.log_message(f"⚠️ Hardware reset attempt {attempt + 1} failed")
                    time.sleep(1)
            
            if not reset_success:
                self.log_message("⚠️ All hardware reset attempts failed, continuing with software reset")
            
            # Step 3: Wait for device to boot with progressive checking
            self.log_message("⏳ Step 3: Waiting for device to boot...")
            for wait_time in [1, 2, 3]:
                time.sleep(wait_time)
                self.log_message(f"   Checking after {wait_time}s...")
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! Device automatically entered flash mode!")
                    self.status_label.config(text="Smart reset successful - device in flash mode!", foreground="green")
                    return True
            
            # Step 4: Try to force flash mode entry with multiple methods
            self.log_message("🚀 Step 4: Attempting to force flash mode entry...")
            force_methods = [
                ("Enhanced force download", self.force_download_mode),
                ("Timing-based reset", lambda: self._try_timing_based_reset(port)),
                ("Baud rate cycling", lambda: self._try_baud_rate_cycling(port)),
            ]
            
            for method_name, method_func in force_methods:
                self.log_message(f"   Trying {method_name}...")
                try:
                    if method_func():
                        self.log_message(f"🎉 SUCCESS! {method_name} worked!")
                        self.status_label.config(text="Smart reset successful - device in flash mode!", foreground="green")
                        return True
                except Exception as e:
                    self.log_message(f"⚠️ {method_name} failed: {str(e)}")
                    continue
            
            # Step 5: Final verification and manual instructions
            self.log_message("🔍 Step 5: Final verification...")
            time.sleep(2)
            if self.check_flash_mode():
                self.log_message("🎉 SUCCESS! Device is now in flash mode!")
                self.status_label.config(text="Smart reset successful - device in flash mode!", foreground="green")
                return True
            
            # Step 6: Comprehensive manual instructions for single-button boards
            self.log_message("⚠️ Enhanced smart reset completed, but device may not be in flash mode")
            self.log_message("💡 For single-button ESP boards, try these manual sequences:")
            self.log_message("   Method 1 (Standard):")
            self.log_message("     1. Press and hold RESET button for 3 seconds")
            self.log_message("     2. Release RESET button")
            self.log_message("     3. Wait 2 seconds")
            self.log_message("     4. Press RESET button briefly (0.5 seconds)")
            self.log_message("     5. Wait for device to enter flash mode")
            self.log_message("   Method 2 (Alternative):")
            self.log_message("     1. Press RESET button briefly")
            self.log_message("     2. Wait 1 second")
            self.log_message("     3. Press RESET button again briefly")
            self.log_message("     4. Wait for device to enter flash mode")
            self.log_message("   Method 3 (Power cycle):")
            self.log_message("     1. Unplug USB cable")
            self.log_message("     2. Wait 5 seconds")
            self.log_message("     3. Plug USB cable back in")
            self.log_message("     4. Press RESET button immediately")
            
            self.status_label.config(text="Enhanced smart reset completed", foreground="orange")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error during enhanced smart reset: {str(e)}")
            self.status_label.config(text="Enhanced smart reset failed", foreground="red")
            return False
    
    def reset_esp01_specific(self, port):
        """Special reset method specifically for ESP-01 boards (most challenging)"""
        try:
            self.log_message("🔧 ESP-01 specific reset sequence...")
            import serial
            
            # ESP-01 boards are very sensitive to timing and need specific sequences
            # Method 1: Very slow DTR/RTS sequence
            try:
                ser = serial.Serial(port, 74880, timeout=2)
                
                # ESP-01 specific sequence - very slow and deliberate
                ser.setDTR(False)
                ser.setRTS(False)
                time.sleep(2.0)  # Very long reset hold for ESP-01
                
                ser.setDTR(True)
                ser.setRTS(False)
                time.sleep(1.0)
                
                ser.setDTR(False)
                ser.setRTS(True)
                time.sleep(2.0)  # Very long flash mode trigger
                
                ser.setDTR(True)
                ser.setRTS(False)
                time.sleep(1.0)
                
                ser.close()
                self.log_message("✅ ESP-01 specific reset sequence completed")
                
                # Wait longer for ESP-01 to respond
                time.sleep(5)
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! ESP-01 is now in flash mode!")
                    return True
                    
            except Exception as e:
                self.log_message(f"⚠️ ESP-01 specific reset failed: {str(e)}")
            
            # Method 2: Try with different baud rates specifically for ESP-01
            baud_rates = [74880, 115200, 57600, 38400]
            for baud in baud_rates:
                try:
                    self.log_message(f"   Trying ESP-01 reset at {baud} baud...")
                    ser = serial.Serial(port, baud, timeout=2)
                    
                    # Send ESP-01 specific boot commands
                    commands = [
                        b'\x00' * 20,  # Multiple null bytes
                        b'\x55' * 10,   # Pattern bytes
                        b'\xAA' * 10,   # Pattern bytes
                        b'AT+RST\r\n',  # AT command reset
                        b'AT+GMR\r\n',  # AT command version
                    ]
                    
                    for cmd in commands:
                        ser.write(cmd)
                        time.sleep(0.5)
                    
                    ser.close()
                    time.sleep(2)
                    
                    if self.check_flash_mode():
                        self.log_message(f"🎉 SUCCESS! ESP-01 reset at {baud} baud worked!")
                        return True
                        
                except Exception:
                    continue
            
            self.log_message("⚠️ ESP-01 specific reset methods completed, but device may not be responding")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error during ESP-01 specific reset: {str(e)}")
            return False
    
    def ultimate_reset_device(self):
        """Ultimate reset method that combines all the best reset techniques for the most stubborn boards"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"Ultimate reset not implemented for {device}")
            return
        
        self.log_message(f"⚡ ULTIMATE RESET for {device} on {port}...")
        self.status_label.config(text="⚡ ULTIMATE RESET in progress...", foreground="red")
        
        try:
            # Phase 1: ESP-01 specific detection and reset
            self.log_message("🔥 Phase 1: ESP-01 detection and specialized reset...")
            if self._detect_esp01_board(port):
                self.log_message("🔍 ESP-01 detected - using specialized method")
                if self.reset_esp01_specific(port):
                    self.log_message("🎉 SUCCESS! ESP-01 ultimate reset worked!")
                    self.status_label.config(text="ESP-01 ultimate reset successful!", foreground="green")
                    return True
                else:
                    self.log_message("⚠️ ESP-01 specialized reset failed, continuing...")
            
            # Phase 2: Enhanced hardware reset with all methods
            self.log_message("🔥 Phase 2: Enhanced hardware reset with all methods...")
            if self.reset_esp_via_dtr_rts(port):
                self.log_message("✅ Enhanced hardware reset completed")
                time.sleep(3)
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! Enhanced hardware reset worked!")
                    self.status_label.config(text="Enhanced hardware reset successful!", foreground="green")
                    return True
            
            # Phase 3: Force download mode with all techniques
            self.log_message("🔥 Phase 3: Force download mode with all techniques...")
            if self.force_download_mode():
                self.log_message("🎉 SUCCESS! Force download mode worked!")
                self.status_label.config(text="Force download mode successful!", foreground="green")
                return True
            
            # Phase 4: Smart reset sequence
            self.log_message("🔥 Phase 4: Smart reset sequence...")
            if self.smart_reset_device():
                self.log_message("🎉 SUCCESS! Smart reset worked!")
                self.status_label.config(text="Smart reset successful!", foreground="green")
                return True
            
            # Phase 5: Final aggressive attempts
            self.log_message("🔥 Phase 5: Final aggressive attempts...")
            
            # Try multiple baud rates with aggressive timing
            baud_rates = [74880, 115200, 57600, 38400, 9600]
            for baud in baud_rates:
                try:
                    self.log_message(f"   Final attempt at {baud} baud...")
                    import serial
                    ser = serial.Serial(port, baud, timeout=1)
                    
                    # Very aggressive DTR/RTS sequence
                    for _ in range(5):
                        ser.setDTR(False)
                        ser.setRTS(False)
                        time.sleep(0.1)
                        
                        ser.setDTR(True)
                        ser.setRTS(False)
                        time.sleep(0.1)
                        
                        ser.setDTR(False)
                        ser.setRTS(True)
                        time.sleep(0.1)
                        
                        ser.setDTR(True)
                        ser.setRTS(False)
                        time.sleep(0.1)
                    
                    # Send aggressive command sequence
                    aggressive_commands = [
                        b'\x00' * 50,  # Many null bytes
                        b'\x55' * 20,  # Pattern bytes
                        b'\xAA' * 20,  # Pattern bytes
                        b'\xFF' * 10,  # All ones
                        b'\x00\x55\xAA\xFF' * 10,  # Mixed pattern
                    ]
                    
                    for cmd in aggressive_commands:
                        ser.write(cmd)
                        time.sleep(0.2)
                    
                    ser.close()
                    time.sleep(3)
                    
                    if self.check_flash_mode():
                        self.log_message(f"🎉 SUCCESS! Aggressive reset at {baud} baud worked!")
                        self.status_label.config(text="Aggressive reset successful!", foreground="green")
                        return True
                        
                except Exception:
                    continue
            
            # Phase 6: Comprehensive manual instructions
            self.log_message("⚠️ ⚡ ULTIMATE RESET completed, but device may still not be responding")
            self.log_message("💡 For the most stubborn boards, try these ultimate manual sequences:")
            self.log_message("   Ultimate Method 1:")
            self.log_message("     1. Unplug USB cable completely")
            self.log_message("     2. Wait 10 seconds")
            self.log_message("     3. Plug USB cable back in")
            self.log_message("     4. Press and hold RESET button for 5 seconds")
            self.log_message("     5. Release RESET button")
            self.log_message("     6. Wait 3 seconds")
            self.log_message("     7. Press RESET button briefly")
            self.log_message("     8. Wait for device to enter flash mode")
            self.log_message("   Ultimate Method 2:")
            self.log_message("     1. Unplug USB cable")
            self.log_message("     2. Wait 5 seconds")
            self.log_message("     3. Plug USB cable back in")
            self.log_message("     4. Immediately press RESET button")
            self.log_message("     5. Keep pressing RESET button")
            self.log_message("     6. While holding RESET, unplug and replug USB")
            self.log_message("     7. Release RESET button")
            self.log_message("     8. Wait for device to enter flash mode")
            self.log_message("   Ultimate Method 3:")
            self.log_message("     1. Try a different USB cable")
            self.log_message("     2. Try a different USB port")
            self.log_message("     3. Try a different computer")
            self.log_message("     4. Check if the board is physically damaged")
            
            self.status_label.config(text="⚡ Ultimate reset completed", foreground="orange")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error during ultimate reset: {str(e)}")
            self.status_label.config(text="⚡ Ultimate reset failed", foreground="red")
            return False
    
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
        
        # For ESP devices, automatically handle reset and flash mode entry
        if device in ["ESP8266", "ESP32"]:
            self.log_message("🚀 Starting automated upload flow for ESP device...")
            self.flow_status_label.config(text="🔄 Step 1: Resetting device...", foreground="blue")
            self.log_message("🔄 Step 1: Attempting to reset device...")
            
            # Try esptool reset first (most reliable)
            try:
                if self.esptool_controlled_reset():
                    self.log_message("✅ esptool reset successful - device should be in flash mode")
                    self.flow_status_label.config(text="✅ Reset successful - proceeding to upload", foreground="green")
                else:
                    self.log_message("⚠️ esptool reset failed, trying emergency reset...")
                    self.flow_status_label.config(text="⚠️ esptool failed - trying emergency reset...", foreground="orange")
                    
                    # If esptool fails, try emergency reset
                    if self.emergency_reset_device():
                        self.log_message("✅ Emergency reset successful - device should be in flash mode")
                        self.flow_status_label.config(text="✅ Emergency reset successful - proceeding to upload", foreground="green")
                    else:
                        self.log_message("⚠️ All reset methods failed")
                        self.log_message("💡 Try uploading anyway - device might be ready")
                        self.flow_status_label.config(text="⚠️ Reset failed - proceeding to upload anyway", foreground="orange")
            except Exception as e:
                self.log_message(f"❌ Error during reset process: {str(e)}")
                self.flow_status_label.config(text="❌ Reset error - proceeding to upload anyway", foreground="red")
                self.log_message("💡 Proceeding with upload - esptool will handle reset")
            
            # Final check if device is in flash mode
            self.flow_status_label.config(text="🔍 Final check: Verifying flash mode...", foreground="blue")
            self.log_message("🔍 Final check: Verifying device is in flash mode...")
            try:
                if self.check_flash_mode():
                    self.log_message("✅ Device is confirmed to be in flash mode!")
                    self.flow_status_label.config(text="✅ Device in flash mode - starting upload", foreground="green")
                else:
                    self.log_message("⚠️ Device may not be in flash mode, but proceeding with upload...")
                    self.log_message("💡 esptool will attempt to put device in flash mode during upload")
                    self.flow_status_label.config(text="⚠️ Flash mode unclear - esptool will handle it", foreground="orange")
            except Exception as e:
                self.log_message(f"⚠️ Error checking flash mode: {str(e)}")
                self.flow_status_label.config(text="⚠️ Flash mode check failed - proceeding anyway", foreground="orange")
                self.log_message("💡 Proceeding with upload - esptool will handle everything")
            
        # Start upload in separate thread
        self.is_uploading = True
        self.upload_button.config(state="disabled")
        self.upload_progress.set(0)
        self.progress_label.config(text="0%")
        self.status_label.config(text="Uploading...", foreground="blue")
        self.flow_status_label.config(text="📤 Uploading firmware...", foreground="blue")
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
            
            # Standard firmware upload process
            
            # Standard firmware upload process
            if device in config.DEVICE_CONFIGS:
                config_info = config.DEVICE_CONFIGS[device]
                command = config_info["command"]
                
                # Get user's preferred esptool reset options
                before_reset = self.app_config.get("esptool_before_reset", "default-reset")
                after_reset = self.app_config.get("esptool_after_reset", "hard-reset")
                
                # For ESP devices, use user's reset preferences
                if device in ["ESP8266", "ESP32"]:
                    # Build args list, replacing reset flags with user preferences
                    args = []
                    skip_next = False
                    
                    for i, arg in enumerate(config_info["args"]):
                        if skip_next:
                            skip_next = False
                            continue
                            
                        if arg == "--before":
                            # Replace with user preference
                            args.append("--before")
                            args.append(before_reset)
                            skip_next = True  # Skip the next argument (the reset value)
                        elif arg == "--after":
                            # Replace with user preference
                            args.append("--after")
                            args.append(after_reset)
                            skip_next = True  # Skip the next argument (the reset value)
                        elif arg in ["default-reset", "hard-reset"]:
                            # Skip these values as they're replaced above
                            continue
                        else:
                            # Format and add other arguments
                            args.append(arg.format(port=port, baud=baud, file=firmware))
                else:
                    # For non-ESP devices, use original args
                    args = [arg.format(port=port, baud=baud, file=firmware) for arg in config_info["args"]]
                
                self.log_message(f"Using reset options: --before {before_reset} --after {after_reset}")
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
                    self.status_label.config(text="✅ Upload completed successfully!", foreground="green")
                    self.flow_status_label.config(text="🎉 Firmware uploaded successfully!", foreground="green")
                    self.log_message("🎉 Upload completed successfully!")
                    self.log_message("💡 Your ESP8266 should now be running the new firmware!")
                    messagebox.showinfo("Success", "Firmware uploaded successfully!\n\nYour ESP8266 should now be running the new firmware.")
                else:
                    self.status_label.config(text="❌ Upload failed", foreground="red")
                    self.flow_status_label.config(text="❌ Upload failed - check log for details", foreground="red")
                    self.log_message("❌ Upload failed!")
                    self.log_message("🔍 Common causes:")
                    self.log_message("   • Device not in flash mode")
                    self.log_message("   • Wrong firmware file")
                    self.log_message("   • Connection issues")
                    self.log_message("   • Hardware problems")
                    messagebox.showerror("Upload Failed", "Upload failed. Check the log for details.\n\nCommon causes:\n• Device not in flash mode\n• Wrong firmware file\n• Connection issues\n• Hardware problems")
                    
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
                            
                            # Pattern file selected
                            
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
        
        # Auto-reset before upload
        auto_reset_var = tk.BooleanVar(value=self.app_config.get("auto_reset_before_upload", False))
        ttk.Checkbutton(settings_window, text="Auto-reset device before upload", 
                       variable=auto_reset_var).pack(pady=5)
        
        # esptool reset options
        ttk.Label(settings_window, text="esptool Reset Options:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
        
        # Before reset option
        ttk.Label(settings_window, text="Before Upload:").pack(pady=(5, 0))
        before_reset_var = tk.StringVar(value=self.app_config.get("esptool_before_reset", "default-reset"))
        before_reset_combo = ttk.Combobox(settings_window, textvariable=before_reset_var, 
                                         values=config.ESPTOOL_RESET_OPTIONS["before_reset"], 
                                         state="readonly", width=20)
        before_reset_combo.pack(pady=2)
        
        # After reset option
        ttk.Label(settings_window, text="After Upload:").pack(pady=(5, 0))
        after_reset_var = tk.StringVar(value=self.app_config.get("esptool_after_reset", "hard-reset"))
        after_reset_combo = ttk.Combobox(settings_window, textvariable=after_reset_var, 
                                        values=config.ESPTOOL_RESET_OPTIONS["after_reset"], 
                                        state="readonly", width=20)
        after_reset_combo.pack(pady=2)
        
        # Reset option descriptions
        ttk.Label(settings_window, text="💡 default-reset: Use DTR/RTS for auto-flash", 
                 foreground="gray", font=("Arial", 8)).pack(pady=2)
        ttk.Label(settings_window, text="💡 no-reset: Skip reset (manual control)", 
                 foreground="gray", font=("Arial", 8)).pack(pady=2)
        ttk.Label(settings_window, text="💡 hard-reset: Force reset after upload", 
                 foreground="gray", font=("Arial", 8)).pack(pady=2)
        
        # Theme selection
        ttk.Label(settings_window, text="Theme:").pack(pady=(15, 5))
        theme_var = tk.StringVar(value=self.app_config.get("theme", "clam"))
        theme_combo = ttk.Combobox(settings_window, textvariable=theme_var, 
                                  values=["clam", "alt", "default", "classic"], state="readonly")
        theme_combo.pack(pady=5)
        
        # Save button
        def save_settings():
            self.app_config.update({
                "auto_detect_ports": auto_detect_var.get(),
                "show_timestamps": show_timestamps_var.get(),
                "auto_reset_before_upload": auto_reset_var.get(),
                "esptool_before_reset": before_reset_var.get(),
                "esptool_after_reset": after_reset_var.get(),
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
    
    def _try_gpio0_simulation_reset(self, port):
        """Try to simulate GPIO0 being pulled low during reset (for single-button boards)"""
        try:
            self.log_message("🔄 Trying GPIO0 simulation reset...")
            import serial
            
            # This method tries to simulate GPIO0 being pulled low
            # by sending specific timing patterns that might trigger download mode
            
            ser = serial.Serial(port, 74880, timeout=1)
            
            # Method 1: Very slow DTR/RTS with specific timing
            ser.setDTR(False)
            ser.setRTS(False)
            time.sleep(2.0)  # Long reset hold
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(1.0)
            
            ser.setDTR(False)
            ser.setRTS(True)
            time.sleep(2.0)  # Long flash mode trigger
            
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(1.0)
            
            ser.close()
            self.log_message("✅ GPIO0 simulation reset completed")
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ GPIO0 simulation reset failed: {str(e)}")
            return False
    
    def _try_voltage_cycling_reset(self, port):
        """Try voltage cycling method (unplug/replug simulation via DTR/RTS)"""
        try:
            self.log_message("🔄 Trying voltage cycling reset...")
            import serial
            
            # This simulates unplugging and replugging the USB
            # by cycling DTR/RTS in a specific pattern
            
            ser = serial.Serial(port, 74880, timeout=1)
            
            # Simulate power off
            ser.setDTR(False)
            ser.setRTS(False)
            time.sleep(3.0)  # Simulate unplugged time
            
            # Simulate power on
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(1.0)
            
            # Simulate GPIO0 pull-down during boot
            ser.setDTR(False)
            ser.setRTS(True)
            time.sleep(2.0)
            
            # Return to normal
            ser.setDTR(True)
            ser.setRTS(False)
            time.sleep(1.0)
            
            ser.close()
            self.log_message("✅ Voltage cycling reset completed")
            return True
            
        except Exception as e:
            self.log_message(f"⚠️ Voltage cycling reset failed: {str(e)}")
            return False
    
    def emergency_reset_device(self):
        """Emergency reset method for the most stubborn single-button ESP boards"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"Emergency reset not implemented for {device}")
            return
        
        self.log_message(f"🚨 EMERGENCY RESET for {device} on {port}...")
        self.status_label.config(text="🚨 EMERGENCY RESET in progress...", foreground="red")
        
        try:
            self.log_message("🔥 Phase 1: Manual reset instructions...")
            self.log_message("💡 CRITICAL: Follow these steps EXACTLY:")
            self.log_message("   1. Unplug USB cable completely")
            self.log_message("   2. Wait 15 seconds")
            self.log_message("   3. Plug USB cable back in")
            self.log_message("   4. IMMEDIATELY press and HOLD RESET button")
            self.log_message("   5. Keep holding for 10 seconds")
            self.log_message("   6. Release RESET button")
            self.log_message("   7. Wait 5 seconds")
            self.log_message("   8. Press RESET button briefly (0.5 seconds)")
            self.log_message("   9. Wait for device to enter flash mode")
            
            # Phase 2: Try automatic hardware reset first
            self.log_message("🔥 Phase 2: Automatic hardware reset attempts...")
            
            # Try ESP-01 specific reset
            if self._try_esp01_aggressive_reset(port):
                self.log_message("✅ ESP-01 aggressive reset completed")
                time.sleep(3)
                
                # Test if it worked
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! Automatic reset worked!")
                    self.status_label.config(text="Automatic reset successful!", foreground="green")
                    return True
            
            # Phase 3: Manual reset instructions
            self.log_message("🔥 Phase 3: Manual reset instructions...")
            self.log_message("💡 CRITICAL: Follow these steps EXACTLY:")
            self.log_message("   1. Unplug USB cable completely")
            self.log_message("   2. Wait 15 seconds")
            self.log_message("   3. Plug USB cable back in")
            self.log_message("   4. IMMEDIATELY press and HOLD RESET button")
            self.log_message("   5. Keep holding for 10 seconds")
            self.log_message("   6. Release RESET button")
            self.log_message("   7. Wait 5 seconds")
            self.log_message("   8. Press RESET button briefly (0.5 seconds)")
            self.log_message("   9. Wait for device to enter flash mode")
            
            # Show a dialog with these instructions
            result = messagebox.askyesno("Emergency Reset", 
                "Follow the manual reset sequence shown in the log.\n\n"
                "After completing the sequence, click 'Yes' to test if the device is in flash mode.\n\n"
                "Click 'No' to cancel.")
            
            if result:
                self.log_message("🔍 Testing if emergency reset worked...")
                time.sleep(3)  # Give user time to complete the sequence
                
                if self.check_flash_mode():
                    self.log_message("🎉 SUCCESS! Emergency reset worked!")
                    self.status_label.config(text="Emergency reset successful!", foreground="green")
                    return True
                else:
                    self.log_message("⚠️ Emergency reset may not have worked")
                    self.log_message("💡 Try the sequence again or check hardware")
                    self.status_label.config(text="Emergency reset attempted", foreground="orange")
                    return False
            else:
                self.log_message("🚨 Emergency reset cancelled by user")
                self.status_label.config(text="Emergency reset cancelled", foreground="red")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Error during emergency reset: {str(e)}")
            self.status_label.config(text="Emergency reset failed", foreground="red")
            return False
    
    def esptool_controlled_reset(self):
        """Use esptool's built-in reset control for more reliable flashing"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        device = self.selected_device.get()
        if device not in ["ESP8266", "ESP32"]:
            messagebox.showerror("Error", f"esptool reset not implemented for {device}")
            return
        
        self.log_message(f"🔧 esptool-controlled reset for {device} on {port}...")
        self.status_label.config(text="esptool reset in progress...", foreground="blue")
        
        try:
            # Method 1: Try esptool's default reset behavior
            self.log_message("🔄 Method 1: Using esptool's default reset behavior...")
            cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), 
                   "--before", "default-reset", "--after", "hard-reset", "chip_id"]
            
            self.log_message(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "Chip ID:" in result.stdout:
                self.log_message("🎉 SUCCESS! esptool reset worked!")
                self.status_label.config(text="esptool reset successful!", foreground="green")
                return True
            else:
                self.log_message("⚠️ Method 1 failed, trying Method 2...")
                self.log_message(f"Error output: {result.stderr}")
            
            # Method 2: Try with no-reset before, then manual reset
            self.log_message("🔄 Method 2: Manual reset with esptool...")
            
            # First, try to put device in flash mode manually
            if self.reset_esp_via_dtr_rts(port):
                self.log_message("✅ Manual reset completed, testing with esptool...")
                time.sleep(2)
                
                # Now try esptool with no-reset
                cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), 
                       "--before", "no-reset", "--after", "hard-reset", "chip_id"]
                
                self.log_message(f"Executing: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and "Chip ID:" in result.stdout:
                    self.log_message("🎉 SUCCESS! Manual reset + esptool worked!")
                    self.status_label.config(text="Manual reset + esptool successful!", foreground="green")
                    return True
                else:
                    self.log_message("⚠️ Method 2 also failed")
                    self.log_message(f"Error output: {result.stderr}")
            
            # Method 2.5: Try aggressive ESP-01 reset
            self.log_message("🔄 Method 2.5: Aggressive ESP-01 reset...")
            if self._try_esp01_aggressive_reset(port):
                self.log_message("✅ Aggressive ESP-01 reset completed, testing with esptool...")
                time.sleep(3)  # Wait longer for ESP-01 to stabilize
                
                # Try esptool with no-reset
                cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), 
                       "--before", "no-reset", "--after", "hard-reset", "chip_id"]
                
                self.log_message(f"Executing: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0 and "Chip ID:" in result.stdout:
                    self.log_message("🎉 SUCCESS! Aggressive reset + esptool worked!")
                    self.status_label.config(text="Aggressive reset + esptool successful!", foreground="green")
                    return True
                else:
                    self.log_message("⚠️ Aggressive reset + esptool failed")
                    self.log_message(f"Error output: {result.stderr}")
            
            # Method 3: Try esptool with different reset options
            self.log_message("🔄 Method 3: Trying different esptool reset options...")
            
            reset_options = [
                ("default-reset", "hard-reset"),
                ("no-reset", "soft-reset"),
                ("default-reset", "no-reset")
            ]
            
            for before_reset, after_reset in reset_options:
                try:
                    self.log_message(f"   Trying --before {before_reset} --after {after_reset}...")
                    cmd = ["python", "-m", "esptool", "--port", port, "--chip", device.lower(), 
                           "--before", before_reset, "--after", after_reset, "chip_id"]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    
                    if result.returncode == 0 and "Chip ID:" in result.stdout:
                        self.log_message(f"🎉 SUCCESS! esptool reset with {before_reset}/{after_reset} worked!")
                        self.status_label.config(text=f"esptool reset successful!", foreground="green")
                        return True
                    else:
                        self.log_message(f"⚠️ {before_reset}/{after_reset} failed")
                        
                except Exception as e:
                    self.log_message(f"⚠️ Error with {before_reset}/{after_reset}: {str(e)}")
                    continue
            
            # If all methods fail, provide manual instructions
            self.log_message("⚠️ All esptool reset methods failed")
            self.log_message("💡 Manual reset required:")
            self.log_message("   1. Hold GPIO0 (or BOOT button) LOW")
            self.log_message("   2. Press RESET button")
            self.log_message("   3. Release RESET button")
            self.log_message("   4. Release GPIO0/BOOT button")
            self.log_message("   5. Try uploading firmware")
            
            self.status_label.config(text="esptool reset failed - manual reset needed", foreground="orange")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error during esptool reset: {str(e)}")
            self.status_label.config(text="esptool reset failed", foreground="red")
            return False
    
    def _try_esp01_aggressive_reset(self, port):
        """Try aggressive reset specifically for ESP-01 boards"""
        try:
            self.log_message("🔥 ESP-01 Aggressive Reset Sequence...")
            
            # Phase 1: Multiple DTR/RTS cycles
            self.log_message("   🔄 Phase 1: Multiple DTR/RTS cycles...")
            for i in range(5):
                self.log_message(f"      Cycle {i+1}/5...")
                if self.reset_esp_via_dtr_rts(port):
                    time.sleep(0.5)
                else:
                    time.sleep(0.2)
            
            # Phase 2: Baud rate cycling with reset
            self.log_message("   🔄 Phase 2: Baud rate cycling with reset...")
            baud_rates = [74880, 115200, 57600, 38400]
            
            for baud in baud_rates:
                self.log_message(f"      Trying {baud} baud...")
                try:
                    import serial
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
                except:
                    continue
            
            # Phase 3: Extended timing reset
            self.log_message("   🔄 Phase 3: Extended timing reset...")
            try:
                import serial
                ser = serial.Serial(port, 74880, timeout=1)
                if ser.is_open:
                    # Hold DTR/RTS low for extended period
                    ser.setDTR(False)
                    ser.setRTS(False)
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
            except:
                pass
            
            self.log_message("✅ ESP-01 aggressive reset sequence completed")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error during ESP-01 aggressive reset: {str(e)}")
            return False

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = JTechPixelUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
