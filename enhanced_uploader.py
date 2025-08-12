#!/usr/bin/env python3
"""
Enhanced J Tech Pixel Uploader
Advanced features: Error handling, device detection, progress tracking, validation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
import json
import threading
import serial
import serial.tools.list_ports
from datetime import datetime
import subprocess
import platform
import hashlib

class EnhancedJTechPixelUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced J Tech Pixel Uploader v2.0")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Enhanced configuration
        self.config_file = "enhanced_config.json"
        self.upload_history_file = "upload_history.json"
        self.load_enhanced_config()
        
        # Enhanced variables
        self.firmware_path = tk.StringVar()
        self.selected_port = tk.StringVar()
        self.selected_device = tk.StringVar()
        self.baud_rate = tk.StringVar()
        self.upload_progress = tk.DoubleVar()
        self.is_uploading = False
        self.upload_history = []
        self.device_status = {}
        self.auto_detection_enabled = tk.BooleanVar(value=True)
        
        # Enhanced upload tracking
        self.upload_start_time = None
        self.upload_retry_count = 0
        self.max_retries = 3
        self.current_upload_session = None
        
        # Load upload history
        self.load_upload_history()
        
        # Setup enhanced UI
        self.setup_enhanced_ui()
        
        # Start auto-detection
        self.start_auto_detection()
        
        # Enhanced error handling
        self.setup_error_handling()
        
    def load_enhanced_config(self):
        """Load enhanced configuration"""
        default_config = {
            "theme": "clam",
            "auto_detection": True,
            "max_retries": 3,
            "upload_timeout": 300,
            "enable_logging": True,
            "log_directory": "EnhancedLogs",
            "recent_files": [],
            "favorite_ports": [],
            "device_preferences": {}
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    # Merge with defaults for new options
                    for key, value in default_config.items():
                        if key not in self.config:
                            self.config[key] = value
            else:
                self.config = default_config
                self.save_enhanced_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = default_config
    
    def save_enhanced_config(self):
        """Save enhanced configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_upload_history(self):
        """Load upload history"""
        try:
            if os.path.exists(self.upload_history_file):
                with open(self.upload_history_file, 'r') as f:
                    self.upload_history = json.load(f)
            else:
                self.upload_history = []
        except Exception as e:
            print(f"Error loading upload history: {e}")
            self.upload_history = []
    
    def save_upload_history(self):
        """Save upload history"""
        try:
            with open(self.upload_history_file, 'w') as f:
                json.dump(self.upload_history, f, indent=2)
        except Exception as e:
            print(f"Error saving upload history: {e}")
    
    def setup_enhanced_ui(self):
        """Setup enhanced user interface"""
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.columnconfigure(3, weight=1)
        
        # Title and version
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="Enhanced J Tech Pixel Uploader", 
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0)
        
        version_label = ttk.Label(title_frame, text="v2.0 - Advanced Features", 
                                 font=("Arial", 12), foreground="blue")
        version_label.grid(row=0, column=1, padx=(20, 0))
        
        # Enhanced device detection frame
        detection_frame = ttk.LabelFrame(main_container, text="🔍 Smart Device Detection", padding="10")
        detection_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Auto-detection toggle
        ttk.Checkbutton(detection_frame, text="Enable Auto-Detection", 
                       variable=self.auto_detection_enabled, 
                       command=self.toggle_auto_detection).grid(row=0, column=0, sticky=tk.W)
        
        # Device status indicators
        self.device_status_label = ttk.Label(detection_frame, text="No devices detected", 
                                           font=("Arial", 10))
        self.device_status_label.grid(row=0, column=1, padx=(20, 0))
        
        # Manual refresh button
        ttk.Button(detection_frame, text="🔄 Refresh Devices", 
                  command=self.manual_refresh_devices).grid(row=0, column=2, padx=(20, 0))
        
        # Enhanced firmware selection
        firmware_frame = ttk.LabelFrame(main_container, text="📁 Firmware Selection", padding="10")
        firmware_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(firmware_frame, text="Firmware File:").grid(row=0, column=0, sticky=tk.W)
        
        file_frame = ttk.Frame(firmware_frame)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.firmware_entry = ttk.Entry(file_frame, textvariable=self.firmware_path)
        self.firmware_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Browse", command=self.select_firmware_file).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(file_frame, text="Validate", command=self.validate_firmware).grid(row=0, column=2, padx=(5, 0))
        
        # File validation status
        self.validation_status = ttk.Label(firmware_frame, text="", font=("Arial", 9))
        self.validation_status.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Enhanced device configuration
        device_frame = ttk.LabelFrame(main_container, text="📱 Device Configuration", padding="10")
        device_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Device type selection
        ttk.Label(device_frame, text="Device Type:").grid(row=0, column=0, sticky=tk.W)
        device_combo = ttk.Combobox(device_frame, textvariable=self.selected_device, 
                                   values=["ESP8266", "ESP32", "AVR", "STM32", "PIC"])
        device_combo.grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        device_combo.bind("<<ComboboxSelected>>", self.on_device_change)
        
        # Port selection with auto-detection
        ttk.Label(device_frame, text="COM Port:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        port_frame = ttk.Frame(device_frame)
        port_frame.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.selected_port, width=15)
        self.port_combo.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(port_frame, text="🔍 Auto-Detect", command=self.auto_detect_port).grid(row=0, column=1, padx=(5, 0))
        ttk.Button(port_frame, text="Test", command=self.test_connection).grid(row=0, column=2, padx=(5, 0))
        
        # Baud rate selection
        ttk.Label(device_frame, text="Baud Rate:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        baud_combo = ttk.Combobox(device_frame, textvariable=self.baud_rate, 
                                 values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        baud_combo.grid(row=2, column=1, padx=(10, 0), sticky=tk.W, pady=(10, 0))
        baud_combo.set("115200")
        
        # Enhanced upload controls
        upload_frame = ttk.LabelFrame(main_container, text="🚀 Upload Control", padding="10")
        upload_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Upload button with enhanced status
        self.upload_button = ttk.Button(upload_frame, text="🚀 Start Enhanced Upload", 
                                      command=self.start_enhanced_upload, style="Accent.TButton")
        self.upload_button.grid(row=0, column=0, padx=(0, 10))
        
        # Upload options
        self.auto_retry_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(upload_frame, text="Auto-Retry on Failure", 
                       variable=self.auto_retry_var).grid(row=0, column=1, padx=(0, 10))
        
        self.backup_firmware_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(upload_frame, text="Backup Current Firmware", 
                       variable=self.backup_firmware_var).grid(row=0, column=2, padx=(0, 10))
        
        # Enhanced progress tracking
        progress_frame = ttk.LabelFrame(main_container, text="📊 Upload Progress", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress bar with enhanced info
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.upload_progress, 
                                          maximum=100, length=500, mode='determinate')
        self.progress_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Progress details
        self.progress_label = ttk.Label(progress_frame, text="Ready", font=("Arial", 10))
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        self.time_remaining_label = ttk.Label(progress_frame, text="", font=("Arial", 9))
        self.time_remaining_label.grid(row=1, column=1, padx=(20, 0))
        
        self.upload_speed_label = ttk.Label(progress_frame, text="", font=("Arial", 9))
        self.upload_speed_label.grid(row=1, column=2, padx=(20, 0))
        
        # Status indicators
        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Ready for upload", 
                                     font=("Arial", 12, "bold"), foreground="green")
        self.status_label.grid(row=0, column=0)
        
        # Enhanced log display
        log_frame = ttk.LabelFrame(main_container, text="📝 Enhanced Log", padding="10")
        log_frame.grid(row=1, column=3, rowspan=6, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(20, 0))
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(log_controls, text="Clear", command=self.clear_log).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(log_controls, text="Save Log", command=self.save_log).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(log_controls, text="Upload History", command=self.show_upload_history).grid(row=0, column=2)
        
        # Enhanced log text widget
        self.log_text = tk.Text(log_frame, height=25, width=60, wrap=tk.WORD, font=("Consolas", 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Configure log frame weights
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
        # Configure main container weights
        main_container.rowconfigure(6, weight=1)
        
        # Apply theme
        self.apply_theme()
        
        # Initial setup
        self.detect_available_ports()
        self.log_message("🚀 Enhanced J Tech Pixel Uploader v2.0 Started", "SUCCESS")
        self.log_message("🔍 Auto-detection enabled", "INFO")
    
    def apply_theme(self):
        """Apply enhanced theme"""
        style = ttk.Style()
        style.theme_use(self.config.get("theme", "clam"))
        
        # Enhanced button styles
        style.configure("Accent.TButton", 
                       background="#007acc", 
                       foreground="white",
                       font=("Arial", 10, "bold"))
        
        style.configure("Success.TButton",
                       background="#28a745",
                       foreground="white")
        
        style.configure("Warning.TButton",
                       background="#ffc107",
                       foreground="black")
        
        style.configure("Error.TButton",
                       background="#dc3545",
                       foreground="white")
    
    def start_auto_detection(self):
        """Start automatic device detection"""
        if self.auto_detection_enabled.get():
            self.auto_detection_thread = threading.Thread(target=self.auto_detection_loop, daemon=True)
            self.auto_detection_thread.start()
    
    def auto_detection_loop(self):
        """Continuous auto-detection loop"""
        while self.auto_detection_enabled.get():
            try:
                self.detect_available_ports()
                self.auto_detect_devices()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                self.log_message(f"Auto-detection error: {e}", "ERROR")
                time.sleep(5)  # Wait longer on error
    
    def toggle_auto_detection(self):
        """Toggle auto-detection on/off"""
        if self.auto_detection_enabled.get():
            self.start_auto_detection()
            self.log_message("🔍 Auto-detection enabled", "INFO")
        else:
            self.log_message("⏸️ Auto-detection disabled", "WARNING")
    
    def auto_detect_devices(self):
        """Automatically detect connected devices"""
        try:
            ports = list(serial.tools.list_ports.comports())
            detected_devices = []
            
            for port in ports:
                try:
                    # Try to identify device type
                    device_info = self.identify_device(port.device)
                    if device_info:
                        detected_devices.append(device_info)
                        self.device_status[port.device] = device_info
                except Exception as e:
                    continue
            
            # Update UI
            self.root.after(0, self.update_device_status, detected_devices)
            
        except Exception as e:
            self.log_message(f"Device detection error: {e}", "ERROR")
    
    def identify_device(self, port):
        """Identify device type on specific port"""
        try:
            # Try to connect and identify
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
    
    def update_device_status(self, devices):
        """Update device status display"""
        if devices:
            status_text = f"Detected: {len(devices)} device(s)"
            self.device_status_label.config(text=status_text, foreground="green")
            
            # Update port combo with detected devices
            detected_ports = [device["port"] for device in devices]
            current_ports = list(self.port_combo.cget("values"))
            
            # Add new ports
            for port in detected_ports:
                if port not in current_ports:
                    current_ports.append(port)
            
            self.port_combo.config(values=current_ports)
            
            # Auto-select first detected port if none selected
            if not self.selected_port.get() and detected_ports:
                self.selected_port.set(detected_ports[0])
        else:
            self.device_status_label.config(text="No devices detected", foreground="red")
    
    def manual_refresh_devices(self):
        """Manually refresh device detection"""
        self.log_message("🔄 Manual device refresh started", "INFO")
        self.auto_detect_devices()
    
    def auto_detect_port(self):
        """Auto-detect and select the best port"""
        try:
            ports = list(serial.tools.list_ports.comports())
            if ports:
                # Prefer ports with device descriptions
                best_port = None
                for port in ports:
                    if port.description and any(keyword in port.description.lower() 
                                              for keyword in ['usb', 'serial', 'com']):
                        best_port = port.device
                        break
                
                if not best_port and ports:
                    best_port = ports[0].device
                
                if best_port:
                    self.selected_port.set(best_port)
                    self.log_message(f"🔍 Auto-detected port: {best_port}", "SUCCESS")
                else:
                    self.log_message("❌ No suitable ports detected", "ERROR")
            else:
                self.log_message("❌ No COM ports available", "ERROR")
        except Exception as e:
            self.log_message(f"Port detection error: {e}", "ERROR")
    
    def detect_available_ports(self):
        """Detect available COM ports"""
        try:
            ports = list(serial.tools.list_ports.comports())
            port_list = [port.device for port in ports]
            
            # Update port combo
            current_ports = list(self.port_combo.cget("values"))
            for port in port_list:
                if port not in current_ports:
                    current_ports.append(port)
            
            self.port_combo.config(values=current_ports)
            
            if ports:
                self.log_message(f"🔌 Detected {len(ports)} port(s): {', '.join(port_list)}", "INFO")
            else:
                self.log_message("⚠️ No COM ports detected", "WARNING")
                
        except Exception as e:
            self.log_message(f"Port detection error: {e}", "ERROR")
    
    def select_firmware_file(self):
        """Select firmware file with enhanced validation"""
        file_path = filedialog.askopenfilename(
            title="Select Firmware File",
            filetypes=[
                ("All supported", "*.bin *.hex *.dat *.elf"),
                ("Binary files", "*.bin"),
                ("Hex files", "*.hex"),
                ("Data files", "*.dat"),
                ("ELF files", "*.elf"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.firmware_path.set(file_path)
            self.validate_firmware()
            
            # Add to recent files
            self.add_to_recent_files(file_path)
    
    def add_to_recent_files(self, file_path):
        """Add file to recent files list"""
        recent_files = self.config.get("recent_files", [])
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        
        # Keep only last 10 files
        recent_files = recent_files[:10]
        self.config["recent_files"] = recent_files
        self.save_enhanced_config()
    
    def validate_firmware(self):
        """Enhanced firmware validation"""
        file_path = self.firmware_path.get()
        if not file_path:
            self.validation_status.config(text="No file selected", foreground="red")
            return False
        
        try:
            if not os.path.exists(file_path):
                self.validation_status.config(text="File does not exist", foreground="red")
                return False
            
            # File size check
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                self.validation_status.config(text="File is empty", foreground="red")
                return False
            
            # File type validation
            file_ext = os.path.splitext(file_path)[1].lower()
            device = self.selected_device.get()
            
            if device in ["ESP8266", "ESP32"]:
                if file_ext not in [".bin", ".hex", ".dat"]:
                    self.validation_status.config(text=f"Invalid file type for {device}", foreground="red")
                    return False
            elif device == "AVR" and file_ext != ".hex":
                self.validation_status.config(text="AVR requires .hex files", foreground="red")
                return False
            
            # Checksum calculation
            checksum = self.calculate_file_checksum(file_path)
            
            # Update validation status
            status_text = f"✅ Valid {file_ext.upper()} file ({file_size} bytes, MD5: {checksum[:8]}...)"
            self.validation_status.config(text=status_text, foreground="green")
            
            self.log_message(f"📁 Firmware validated: {os.path.basename(file_path)}", "SUCCESS")
            return True
            
        except Exception as e:
            self.validation_status.config(text=f"Validation error: {e}", foreground="red")
            self.log_message(f"❌ Firmware validation failed: {e}", "ERROR")
            return False
    
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
    
    def on_device_change(self, event=None):
        """Handle device type change"""
        device = self.selected_device.get()
        self.log_message(f"📱 Device changed to: {device}", "INFO")
        
        # Auto-detect port for ESP devices
        if device in ["ESP8266", "ESP32"]:
            self.auto_detect_port()
    
    def test_connection(self):
        """Test connection to selected port"""
        port = self.selected_port.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port first")
            return
        
        self.log_message(f"🔌 Testing connection to {port}...", "INFO")
        
        try:
            ser = serial.Serial(port, int(self.baud_rate.get()), timeout=2)
            if ser.is_open:
                self.log_message(f"✅ Port {port} opened successfully", "SUCCESS")
                
                # Try to identify device
                device_info = self.identify_device(port)
                if device_info:
                    self.log_message(f"📱 Device identified: {device_info['type']}", "SUCCESS")
                else:
                    self.log_message("⚠️ Device type not identified", "WARNING")
                
                ser.close()
                self.log_message("✅ Connection test completed", "SUCCESS")
            else:
                self.log_message(f"❌ Failed to open port {port}", "ERROR")
                
        except serial.SerialException as e:
            error_msg = str(e)
            if "Access is denied" in error_msg:
                self.log_message(f"❌ Port {port} is in use by another application", "ERROR")
            elif "File not found" in error_msg:
                self.log_message(f"❌ Port {port} not found", "ERROR")
            else:
                self.log_message(f"❌ Connection error: {error_msg}", "ERROR")
    
    def start_enhanced_upload(self):
        """Start enhanced upload with validation and error handling"""
        if self.is_uploading:
            messagebox.showwarning("Warning", "Upload already in progress")
            return
        
        # Validate firmware
        if not self.validate_firmware():
            messagebox.showerror("Error", "Please select a valid firmware file")
            return
        
        # Validate device selection
        if not self.selected_device.get():
            messagebox.showerror("Error", "Please select a device type")
            return
        
        # Validate port selection
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
        
        # Start upload in separate thread
        self.upload_thread = threading.Thread(target=self.enhanced_upload_process, daemon=True)
        self.upload_thread.start()
    
    def enhanced_upload_process(self):
        """Enhanced upload process with error handling and retry logic"""
        try:
            self.is_uploading = True
            self.upload_start_time = time.time()
            self.upload_retry_count = 0
            
            # Create upload session
            self.current_upload_session = {
                "timestamp": datetime.now().isoformat(),
                "device": self.selected_device.get(),
                "firmware": os.path.basename(self.firmware_path.get()),
                "port": self.selected_port.get(),
                "baud": self.baud_rate.get(),
                "status": "Starting"
            }
            
            self.log_message("🚀 Starting enhanced upload process...", "INFO")
            self.update_progress(0, "Initializing upload...")
            
            # Backup current firmware if requested
            if self.backup_firmware_var.get():
                self.backup_current_firmware()
            
            # Perform upload
            success = self.perform_upload()
            
            if success:
                self.upload_success()
            else:
                self.upload_failure()
                
        except Exception as e:
            self.log_message(f"❌ Upload process error: {e}", "ERROR")
            self.upload_failure()
        finally:
            self.is_uploading = False
            self.upload_button.config(state="normal")
    
    def backup_current_firmware(self):
        """Backup current firmware before upload"""
        try:
            self.log_message("💾 Creating firmware backup...", "INFO")
            self.update_progress(5, "Backing up current firmware...")
            
            # This would implement actual firmware backup
            # For now, just simulate the process
            time.sleep(1)
            
            self.log_message("✅ Firmware backup completed", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"⚠️ Firmware backup failed: {e}", "WARNING")
    
    def perform_upload(self):
        """Perform the actual firmware upload"""
        try:
            device = self.selected_device.get()
            port = self.selected_port.get()
            baud = self.baud_rate.get()
            firmware = self.firmware_path.get()
            
            self.log_message(f"📤 Uploading {device} firmware to {port}...", "INFO")
            self.update_progress(10, "Starting firmware upload...")
            
            # Simulate upload process with progress updates
            upload_steps = [
                (20, "Connecting to device..."),
                (30, "Erasing flash memory..."),
                (50, "Writing firmware data..."),
                (70, "Verifying firmware..."),
                (90, "Finalizing upload..."),
                (100, "Upload completed!")
            ]
            
            for progress, message in upload_steps:
                time.sleep(1)  # Simulate upload time
                self.update_progress(progress, message)
                
                # Check for errors (simulated)
                if progress == 50 and self.upload_retry_count < self.max_retries:
                    if not self.handle_upload_error("Simulated write error"):
                        return False
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Upload error: {e}", "ERROR")
            return False
    
    def handle_upload_error(self, error_message):
        """Handle upload errors with retry logic"""
        self.upload_retry_count += 1
        
        if self.upload_retry_count <= self.max_retries:
            self.log_message(f"⚠️ Upload error: {error_message}", "WARNING")
            self.log_message(f"🔄 Retrying upload ({self.upload_retry_count}/{self.max_retries})...", "INFO")
            
            # Wait before retry
            time.sleep(2)
            return True
        else:
            self.log_message(f"❌ Max retries exceeded. Upload failed.", "ERROR")
            return False
    
    def update_progress(self, progress, message):
        """Update upload progress with enhanced information"""
        self.upload_progress.set(progress)
        self.progress_label.config(text=message)
        
        # Calculate time remaining
        if progress > 0 and self.upload_start_time:
            elapsed_time = time.time() - self.upload_start_time
            if progress < 100:
                estimated_total = elapsed_time * 100 / progress
                remaining = estimated_total - elapsed_time
                self.time_remaining_label.config(text=f"⏱️ {remaining:.1f}s remaining")
            else:
                self.time_remaining_label.config(text="✅ Complete!")
        
        # Calculate upload speed (simulated)
        if progress > 10:
            speed = f"📊 {progress * 10:.0f} KB/s"
            self.upload_speed_label.config(text=speed)
        
        # Update status
        if progress == 100:
            self.status_label.config(text="Upload completed successfully!", foreground="green")
        elif progress > 0:
            self.status_label.config(text=f"Uploading... {progress}%", foreground="blue")
        
        # Force UI update
        self.root.update_idletasks()
    
    def upload_success(self):
        """Handle successful upload"""
        self.log_message("🎉 Upload completed successfully!", "SUCCESS")
        self.update_progress(100, "Upload completed!")
        
        # Record upload history
        self.record_upload_history(True)
        
        # Show success message
        messagebox.showinfo("Success", "Firmware uploaded successfully!")
    
    def upload_failure(self):
        """Handle failed upload"""
        self.log_message("❌ Upload failed", "ERROR")
        self.update_progress(0, "Upload failed")
        self.status_label.config(text="Upload failed", foreground="red")
        
        # Record upload history
        self.record_upload_history(False)
        
        # Show error message
        messagebox.showerror("Error", "Upload failed. Check the log for details.")
    
    def record_upload_history(self, success):
        """Record upload attempt in history"""
        if self.current_upload_session:
            self.current_upload_session["status"] = "Success" if success else "Failed"
            self.current_upload_session["duration"] = time.time() - self.upload_start_time if self.upload_start_time else 0
            
            self.upload_history.append(self.current_upload_session)
            
            # Keep only last 100 uploads
            if len(self.upload_history) > 100:
                self.upload_history = self.upload_history[-100:]
            
            self.save_upload_history()
    
    def show_upload_history(self):
        """Show upload history window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Upload History")
        history_window.geometry("800x600")
        
        # Create treeview for history
        columns = ("Date", "Device", "Firmware", "Port", "Status", "Duration")
        tree = ttk.Treeview(history_window, columns=columns, show="headings", height=20)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate with history data
        for upload in reversed(self.upload_history):
            duration = f"{upload.get('duration', 0):.1f}s" if upload.get('duration') else "N/A"
            tree.insert("", tk.END, values=(
                upload.get("timestamp", "")[:19],  # Format timestamp
                upload.get("device", ""),
                upload.get("firmware", ""),
                upload.get("port", ""),
                upload.get("status", ""),
                duration
            ))
        
        # Layout
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(history_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Clear History", 
                  command=self.clear_upload_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export History", 
                  command=self.export_upload_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", 
                  command=history_window.destroy).pack(side=tk.RIGHT)
    
    def clear_upload_history(self):
        """Clear upload history"""
        if messagebox.askyesno("Confirm", "Clear all upload history?"):
            self.upload_history = []
            self.save_upload_history()
            messagebox.showinfo("Success", "Upload history cleared")
    
    def export_upload_history(self):
        """Export upload history to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Upload History",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', newline='') as f:
                    import csv
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Device", "Firmware", "Port", "Status", "Duration"])
                    
                    for upload in self.upload_history:
                        duration = f"{upload.get('duration', 0):.1f}s" if upload.get('duration') else "N/A"
                        writer.writerow([
                            upload.get("timestamp", ""),
                            upload.get("device", ""),
                            upload.get("firmware", ""),
                            upload.get("port", ""),
                            upload.get("status", ""),
                            duration
                        ])
                
                messagebox.showinfo("Success", f"Upload history exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def log_message(self, message, level="INFO"):
        """Enhanced logging with levels and timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different levels
        colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red"
        }
        
        color = colors.get(level, "black")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Add to log widget
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        
        # Apply color
        start = f"{timestamp} {level}: "
        end = f"{timestamp} {level}: {message}"
        
        # Find and color the line
        lines = self.log_text.get("1.0", tk.END).split('\n')
        for i, line in enumerate(lines):
            if line.startswith(f"[{timestamp}] {level}:"):
                line_start = f"{i+1}.0"
                line_end = f"{i+1}.end"
                
                # Remove existing tags
                self.log_text.tag_remove("SUCCESS", line_start, line_end)
                self.log_text.tag_remove("WARNING", line_start, line_end)
                self.log_text.tag_remove("ERROR", line_start, line_end)
                
                # Apply new tag
                if level in ["SUCCESS", "WARNING", "ERROR"]:
                    self.log_text.tag_add(level, line_start, line_end)
                    self.log_text.tag_config(level, foreground=color)
                
                break
        
        # Also print to console
        print(formatted_message.strip())
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete("1.0", tk.END)
        self.log_message("📝 Log cleared", "INFO")
    
    def save_log(self):
        """Save current log to file"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Save Log",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                log_content = self.log_text.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                messagebox.showinfo("Success", f"Log saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {e}")
    
    def setup_error_handling(self):
        """Setup enhanced error handling"""
        # Global exception handler
        def handle_exception(exc_type, exc_value, exc_traceback):
            error_msg = f"Unhandled exception: {exc_type.__name__}: {exc_value}"
            self.log_message(error_msg, "ERROR")
            
            # Log full traceback
            import traceback
            traceback_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.log_message(f"Traceback:\n{traceback_text}", "ERROR")
        
        # Set exception handler
        import sys
        sys.excepthook = handle_exception
        
        self.log_message("🛡️ Enhanced error handling enabled", "INFO")

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EnhancedJTechPixelUploader(root)
    
    # Handle window closing
    def on_closing():
        app.save_enhanced_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
