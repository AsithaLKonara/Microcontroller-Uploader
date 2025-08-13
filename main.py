import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial.tools.list_ports
import subprocess
import os
import threading
import time
from datetime import datetime

class JTechPixelUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("J Tech Pixel Uploader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.firmware_path = tk.StringVar()
        self.selected_port = tk.StringVar()
        self.selected_device = tk.StringVar(value="ESP8266")
        self.baud_rate = tk.StringVar(value="115200")
        self.upload_progress = tk.DoubleVar()
        self.is_uploading = False
        
        # Device configurations
        self.device_configs = {
                    "ESP8266": {
            "command": "python",
            "args": ["-m", "esptool", "--port", "{port}", "--baud", "{baud}", "write-flash", "--flash-mode", "dio", "--flash-size", "detect", "0x00000", "{file}"],
            "description": "ESP8266 NodeMCU, Wemos D1 Mini",
            "supported_formats": [".bin"],
            "flash_offsets": {
                "single_bin": ["0x00000"],
                "bootloader_app": ["0x00000", "0x1000"],
                "full_system": ["0x00000", "0x1000", "0x300000"]
            }
        },
                    "ESP32": {
            "command": "python",
            "args": ["-m", "esptool", "--chip", "esp32", "--port", "{port}", "--baud", "{baud}", "write-flash", "--flash-mode", "dio", "--flash-size", "detect", "0x1000", "{file}"],
            "description": "ESP32 DevKit, ESP32-WROOM",
            "supported_formats": [".bin"],
            "flash_offsets": {
                "single_bin": ["0x1000"],
                "bootloader_app": ["0x1000", "0x8000", "0x10000"]
            }
        },
            "AVR": {
                "command": "avrdude",
                "args": ["-c", "arduino", "-p", "atmega328p", "-P", "{port}", "-b", "{baud}", "-U", "flash:w:{file}:i"],
                "description": "Arduino Uno, Nano, Pro Mini",
                "supported_formats": [".hex", ".bin"],
                "flash_offsets": {}
            },
            "STM32": {
                "command": "stm32flash",
                "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
                "description": "STM32F103, STM32F407",
                "supported_formats": [".bin", ".hex"],
                "flash_offsets": {}
            }
        }
        
        self.setup_ui()
        self.detect_ports()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="J Tech Pixel Uploader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Firmware file selection
        ttk.Label(main_frame, text="Firmware File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        file_entry = ttk.Entry(main_frame, textvariable=self.firmware_path, width=50)
        file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        file_button_frame = ttk.Frame(main_frame)
        file_button_frame.grid(row=1, column=2, pady=5)
        ttk.Button(file_button_frame, text="Browse", command=self.select_firmware_file).grid(row=0, column=0)
        ttk.Button(file_button_frame, text="?", command=self.show_firmware_help, width=3).grid(row=0, column=1, padx=(5, 0))
        
        # Device type selection
        ttk.Label(main_frame, text="Device Type:").grid(row=2, column=0, sticky=tk.W, pady=5)
        device_frame = ttk.Frame(main_frame)
        device_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        device_combo = ttk.Combobox(device_frame, textvariable=self.selected_device, 
                                   values=list(self.device_configs.keys()), state="readonly", width=20)
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
        
        # Baud rate selection
        ttk.Label(main_frame, text="Baud Rate:").grid(row=4, column=0, sticky=tk.W, pady=5)
        baud_combo = ttk.Combobox(main_frame, textvariable=self.baud_rate, 
                                 values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"], 
                                 state="readonly", width=20)
        baud_combo.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.upload_button = ttk.Button(button_frame, text="Upload Firmware", 
                                       command=self.start_upload, style="Accent.TButton")
        self.upload_button.grid(row=0, column=0, padx=(0, 10))
        
        self.test_button = ttk.Button(button_frame, text="Test Connection", 
                                     command=self.test_connection)
        self.test_button.grid(row=0, column=1, padx=10)
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="About", command=self.show_about).grid(row=0, column=3, padx=10)
        
        # Progress bar
        ttk.Label(main_frame, text="Upload Progress:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.upload_progress, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(20, 5))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Log output
        ttk.Label(main_frame, text="Upload Log:").grid(row=8, column=0, sticky=tk.W, pady=(20, 5))
        
        # Log frame with scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget and scrollbar
        self.log_text = tk.Text(log_frame, height=15, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(9, weight=1)
        
        # Initial device description
        self.on_device_change()
        
    def select_firmware_file(self):
        device = self.selected_device.get()
        if device in self.device_configs:
            config = self.device_configs[device]
            supported_formats = config.get("supported_formats", [])
            
            if supported_formats:
                # Create file type filter for supported formats
                filetypes = [
                    (f"Supported formats ({', '.join(supported_formats)})", " ".join(supported_formats)),
                    ("All files", "*.*")
                ]
            else:
                filetypes = [
                    ("Firmware files", "*.bin *.hex *.dat *.elf"),
                    ("Binary files", "*.bin"),
                    ("Hex files", "*.hex"),
                    ("All files", "*.*")
                ]
        else:
            filetypes = [
                ("Firmware files", "*.bin *.hex *.dat *.elf"),
                ("Binary files", "*.bin"),
                ("Hex files", "*.hex"),
                ("All files", "*.*")
            ]
            
        filename = filedialog.askopenfilename(title="Select Firmware File", filetypes=filetypes)
        if filename:
            # Validate the selected file
            if self.validate_firmware_file(filename):
                self.firmware_path.set(filename)
                self.log_message(f"Selected firmware: {os.path.basename(filename)}")
            else:
                messagebox.showerror("Invalid Firmware", 
                    f"This file type is not compatible with {device} devices.\n\n"
                    f"Supported formats: {', '.join(supported_formats) if 'supported_formats' in config else 'All formats'}")
    
    def validate_firmware_file(self, filepath):
        """Validate that the firmware file is compatible with the selected device"""
        device = self.selected_device.get()
        if device not in self.device_configs:
            return True  # Can't validate unknown device
            
        config = self.device_configs[device]
        supported_formats = config.get("supported_formats", [])
        
        if not supported_formats:
            return True  # No restrictions
            
        file_ext = os.path.splitext(filepath)[1].lower()
        
        # Check if file extension is supported
        if file_ext not in supported_formats:
            return False
            
        # Additional validation for ESP devices
        if device.startswith("ESP"):
            if file_ext == ".hex":
                self.log_message("⚠ Warning: .hex files are not valid for ESP chips. Use .bin instead.")
                return False
            elif file_ext == ".bin":
                # Check if it's a valid ESP binary (basic size check)
                try:
                    file_size = os.path.getsize(filepath)
                    if file_size < 1024:  # Less than 1KB is suspicious
                        self.log_message("⚠ Warning: Binary file seems too small for ESP firmware")
                    elif file_size > 16 * 1024 * 1024:  # More than 16MB is suspicious
                        self.log_message("⚠ Warning: Binary file seems too large for ESP firmware")
                except:
                    pass
                    
        return True
            
    def detect_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if ports:
            self.selected_port.set(ports[0])
            self.log_message(f"Detected {len(ports)} COM port(s): {', '.join(ports)}")
        else:
            self.log_message("No COM ports detected")
            
    def on_device_change(self):
        device = self.selected_device.get()
        if device in self.device_configs:
            config = self.device_configs[device]
            desc = config["description"]
            self.device_desc_label.config(text=desc)
            
            # Show format restrictions
            supported_formats = config.get("supported_formats", [])
            if supported_formats:
                format_info = f"Supported formats: {', '.join(supported_formats)}"
                self.log_message(f"Selected device: {device} - {desc}")
                self.log_message(f"📋 {format_info}")
                
                # Show special warnings for ESP devices
                if device.startswith("ESP"):
                    self.log_message("⚠ Important: ESP devices only support .bin files, not .hex files")
                    self.log_message("💡 If you have a .hex file, you need to convert it to .bin first")
            else:
                self.log_message(f"Selected device: {device} - {desc}")
                self.log_message("📋 All firmware formats supported")
            
    def start_upload(self):
        if self.is_uploading:
            return
            
        # Validate inputs
        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a firmware file")
            return
            
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        if not os.path.exists(self.firmware_path.get()):
            messagebox.showerror("Error", "Selected firmware file does not exist")
            return
            
        # Validate firmware compatibility
        if not self.validate_firmware_file(self.firmware_path.get()):
            messagebox.showerror("Error", "Selected firmware is not compatible with the chosen device")
            return
            
        # Start upload in separate thread
        self.is_uploading = True
        self.upload_button.config(state="disabled")
        self.upload_progress.set(0)
        self.status_label.config(text="Uploading...", foreground="blue")
        
        upload_thread = threading.Thread(target=self.upload_firmware)
        upload_thread.daemon = True
        upload_thread.start()
        
    def upload_firmware(self):
        try:
            device = self.selected_device.get()
            port = self.selected_port.get()
            baud = self.baud_rate.get()
            firmware = self.firmware_path.get()
            
            self.log_message(f"Starting upload for {device} on {port} at {baud} baud")
            self.log_message(f"Firmware: {os.path.basename(firmware)}")
            
            command, args = self.get_flash_command(device, port, baud, firmware)
            
            if command:
                self.log_message(f"Executing: {command} {' '.join(args)}")
                
                # Run the upload command (hide terminal window on Windows)
                startupinfo = None
                if os.name == 'nt':  # Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen([command] + args, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True,
                                         bufsize=1,
                                         startupinfo=startupinfo)
                
                # Monitor output with live progress updates
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        output = output.strip()
                        self.log_message(output)
                        
                        # Live progress updates from esptool output
                        if "Writing at" in output and "%" in output:
                            try:
                                # Extract percentage from "Writing at 0x00000000 [==============] 100.0% 18/18 bytes..."
                                percent_str = output.split("%")[0].split()[-1]
                                percent = float(percent_str)
                                self.upload_progress.set(percent)
                            except:
                                pass
                        elif "Compressed" in output:
                            # Show compression progress
                            self.upload_progress.set(25)
                        elif "Uploading stub flasher" in output:
                            # Show stub upload progress
                            self.upload_progress.set(10)
                        elif "Running stub flasher" in output:
                            # Show stub running progress
                            self.upload_progress.set(35)
                        elif "Configuring flash size" in output:
                            # Show flash configuration progress
                            self.upload_progress.set(50)
                        elif "Writing" in output and "bytes" in output:
                            # Show writing progress
                            self.upload_progress.set(75)
                
                return_code = process.poll()
                
                if return_code == 0:
                    self.upload_progress.set(100)
                    
                    # Post-upload verification for ESP devices
                    if device.startswith("ESP"):
                        verification_result = self.verify_esp_upload(port, baud)
                        if verification_result:
                            self.status_label.config(text="Upload completed successfully! ✅", foreground="green")
                            self.log_message("✅ Upload completed successfully! ESP device should now be running the firmware.")
                            messagebox.showinfo("Success", "Firmware uploaded successfully!\n\nESP device should now be running the new firmware.\n\nIf the LED pattern isn't working, check:\n• Hardware wiring (GPIO pin connections)\n• Power supply stability\n• Reset the board after upload")
                        else:
                            self.status_label.config(text="Upload completed but verification failed ⚠", foreground="orange")
                            self.log_message("⚠ Upload completed but ESP verification failed. Device may not be running firmware.")
                            messagebox.showwarning("Upload Complete", "Firmware uploaded successfully!\n\nHowever, ESP verification failed.\nThe device may not be running the new firmware.\n\nTroubleshooting:\n• Check if device is in flash mode (GPIO0)\n• Verify power supply\n• Try resetting the board")
                    else:
                        self.status_label.config(text="Upload completed successfully!", foreground="green")
                        self.log_message("✅ Upload completed successfully!")
                        messagebox.showinfo("Success", "Firmware uploaded successfully!")
                else:
                    self.status_label.config(text="Upload failed", foreground="red")
                    self.log_message("❌ Upload failed!")
                    messagebox.showerror("Error", "Upload failed. Check the log for details.")
                    
            else:
                self.log_message(f"❌ Device type '{device}' not supported or no flash command found.")
                messagebox.showerror("Error", f"Device type '{device}' not supported or no flash command found.")
                
        except Exception as e:
            self.log_message(f"❌ Error during upload: {str(e)}")
            self.status_label.config(text="Upload error", foreground="red")
            messagebox.showerror("Error", f"Upload error: {str(e)}")
            
        finally:
            self.is_uploading = False
            self.upload_button.config(state="normal")
            
    def get_flash_command(self, device, port, baud, firmware):
        """Get the appropriate flash command based on device and firmware type"""
        if device not in self.device_configs:
            return None, None
            
        config = self.device_configs[device]
        command = config["command"]
        
        # For ESP devices, we might need multiple offsets
        if device.startswith("ESP"):
            return self._get_esp_flash_command(config, port, baud, firmware)
        else:
            # For non-ESP devices, use the standard args
            args = [arg.format(port=port, baud=baud, file=firmware) for arg in config["args"]]
            return command, args
    
    def _get_esp_flash_command(self, config, port, baud, firmware):
        """Generate ESP flash command with appropriate offsets"""
        command = config["command"]
        
        # Use the config args and format them with the actual values
        args = [arg.format(port=port, baud=baud, file=firmware) for arg in config["args"]]
        
        return command, args
            
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Update log in main thread
        self.root.after(0, self._update_log, log_entry)
        
    def _update_log(self, message):
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def show_about(self):
        about_text = """J Tech Pixel Uploader v1.0

A professional firmware uploader tool for microcontrollers.

Supported devices:
• ESP8266 (NodeMCU, Wemos D1 Mini)
• ESP32 (DevKit, ESP32-WROOM)
• AVR (Arduino Uno, Nano, Pro Mini)
• STM32 (STM32F103, STM32F407)

Features:
• Easy firmware selection
• Automatic COM port detection
• Multiple device support
• Connection testing before upload
• Real-time upload progress
• Detailed logging
• Smart file validation

Built with Python and Tkinter
© 2024 J Tech Pixel"""
        
        messagebox.showinfo("About J Tech Pixel Uploader", about_text)

    def verify_esp_upload(self, port, baud):
        """Verify that ESP device is responding after upload"""
        try:
            self.log_message("🔍 Verifying ESP device response...")
            
            # Try to read chip info to verify device is responding
            command = "python"
            args = ["-m", "esptool", "--port", port, "--baud", baud, "chip_id"]
            
            # Hide terminal window on Windows
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen([command] + args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     universal_newlines=True,
                                     startupinfo=startupinfo)
            
            output, _ = process.communicate()
            return_code = process.returncode
            
            if return_code == 0 and "Chip ID:" in output:
                self.log_message("✅ ESP device verification successful - device is responding")
                return True
            else:
                self.log_message("⚠ ESP device verification failed - device may not be responding")
                self.log_message(f"Verification output: {output.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("⚠ ESP verification timed out - device may be busy or not responding")
            return False
        except Exception as e:
            self.log_message(f"⚠ ESP verification error: {str(e)}")
            return False

    def show_firmware_help(self):
        """Show help information about firmware formats"""
        device = self.selected_device.get()
        
        if device.startswith("ESP"):
            help_text = f"""Firmware Format Help for {device}

⚠ IMPORTANT: {device} devices ONLY support .bin files!

❌ DO NOT use .hex files - they are for Arduino/AVR chips, not ESP chips.

✅ Use .bin files - these are the correct format for ESP devices.

Common issues:
• .hex files upload successfully but don't run
• .hex files are Intel HEX format, not ESP binary format
• ESP bootloader cannot execute .hex files

How to get .bin files:
• Arduino IDE: Sketch → Export Compiled Binary
• PlatformIO: Build → Export Binary
• ESP-IDF: idf.py build
• Download pre-compiled .bin files for your board

If you only have .hex files:
• Recompile your code for ESP8266/ESP32
• Use a hex-to-bin converter (not recommended)
• Find the correct .bin version online"""
        else:
            help_text = f"""Firmware Format Help for {device}

This device supports multiple firmware formats:
• .bin - Binary files (most common)
• .hex - Intel HEX files (Arduino standard)
• .dat - Data files (if applicable)
• .elf - ELF files (debugging)

Select the appropriate format for your firmware source."""
            
        messagebox.showinfo("Firmware Format Help", help_text)

    def test_connection(self):
        """Test if a device is responding on the selected COM port."""
        device = self.selected_device.get()
        port = self.selected_port.get()
        baud = self.baud_rate.get()

        if not port:
            messagebox.showwarning("Warning", "Please select a COM port to test.")
            return

        if not baud:
            messagebox.showwarning("Warning", "Please select a baud rate to test.")
            return

        self.log_message(f"🔍 Testing connection to {device} on {port} at {baud} baud...")
        self.test_button.config(state="disabled", text="Testing...")
        self.status_label.config(text="Testing connection...", foreground="blue")

        # Test connection in separate thread to keep UI responsive
        test_thread = threading.Thread(target=self._test_connection_thread, args=(device, port, baud))
        test_thread.daemon = True
        test_thread.start()

    def _test_connection_thread(self, device, port, baud):
        """Test connection in a separate thread"""
        try:
            if device.startswith("ESP"):
                success = self._test_esp_connection(port, baud)
            elif device == "AVR":
                success = self._test_avr_connection(port, baud)
            elif device == "STM32":
                success = self._test_stm32_connection(port, baud)
            else:
                success = self._test_generic_connection(port, baud)

            # Update UI in main thread
            self.root.after(0, self._update_test_result, success, device, port, baud)

        except Exception as e:
            self.root.after(0, self._update_test_error, str(e))

    def _test_esp_connection(self, port, baud):
        """Test ESP device connection using esptool"""
        try:
            command = "python"
            args = ["-m", "esptool", "--port", port, "--baud", baud, "chip_id"]
            
            # Hide terminal window on Windows
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen([command] + args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     universal_newlines=True,
                                     startupinfo=startupinfo)
            
            output, _ = process.communicate(timeout=10)  # Wait for up to 10 seconds
            return_code = process.returncode

            if return_code == 0 and ("Chip ID:" in output or "Chip type:" in output):
                self.log_message("✅ ESP device detected and responding!")
                self.log_message(f"Device info: {output.strip()}")
                return True
            else:
                self.log_message(f"❌ ESP device not responding or error occurred.")
                self.log_message(f"Output: {output.strip()}")
                return False

        except subprocess.TimeoutExpired:
            self.log_message("⚠ ESP connection test timed out.")
            return False
        except Exception as e:
            self.log_message(f"❌ ESP connection test error: {str(e)}")
            return False

    def _test_avr_connection(self, port, baud):
        """Test AVR device connection using avrdude"""
        try:
            command = "avrdude"
            args = ["-c", "arduino", "-p", "atmega328p", "-P", port, "-b", baud, "-q"]
            
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen([command] + args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     universal_newlines=True,
                                     startupinfo=startupinfo)
            
            output, _ = process.communicate(timeout=10)
            return_code = process.returncode

            if return_code == 0:
                self.log_message("✅ AVR device detected and responding!")
                return True
            else:
                self.log_message(f"❌ AVR device not responding or error occurred.")
                self.log_message(f"Output: {output.strip()}")
                return False

        except subprocess.TimeoutExpired:
            self.log_message("⚠ AVR connection test timed out.")
            return False
        except Exception as e:
            self.log_message(f"❌ AVR connection test error: {str(e)}")
            return False

    def _test_stm32_connection(self, port, baud):
        """Test STM32 device connection using stm32flash"""
        try:
            command = "stm32flash"
            args = ["-b", baud, port]
            
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen([command] + args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     universal_newlines=True,
                                     startupinfo=startupinfo)
            
            output, _ = process.communicate(timeout=10)
            return_code = process.returncode

            if return_code == 0 and ("STM32" in output or "Chip" in output):
                self.log_message("✅ STM32 device detected and responding!")
                return True
            else:
                self.log_message(f"❌ STM32 device not responding or error occurred.")
                self.log_message(f"Output: {output.strip()}")
                return False

        except subprocess.TimeoutExpired:
            self.log_message("⚠ STM32 connection test timed out.")
            return False
        except Exception as e:
            self.log_message(f"❌ STM32 connection test error: {str(e)}")
            return False

    def _test_generic_connection(self, port, baud):
        """Test generic serial connection"""
        try:
            import serial
            ser = serial.Serial(port, int(baud), timeout=2)
            if ser.is_open:
                ser.close()
                self.log_message("✅ Serial port is accessible!")
                return True
            else:
                self.log_message("❌ Serial port is not accessible.")
                return False
        except Exception as e:
            self.log_message(f"❌ Generic connection test error: {str(e)}")
            return False

    def _update_test_result(self, success, device, port, baud):
        """Update UI with test result"""
        self.test_button.config(state="normal", text="Test Connection")
        
        if success:
            self.status_label.config(text="Connection test successful! ✅", foreground="green")
            messagebox.showinfo("Connection Successful", 
                f"Connection to {device} on {port} at {baud} baud successful!\n\n"
                f"Device is responding and ready for firmware upload.")
        else:
            self.status_label.config(text="Connection test failed ❌", foreground="red")
            messagebox.showwarning("Connection Failed", 
                f"Connection to {device} on {port} at {baud} baud failed.\n\n"
                f"Device not responding or error occurred.\n\n"
                f"Troubleshooting:\n"
                f"• Ensure device is powered on\n"
                f"• Check COM port connection\n"
                f"• Verify baud rate\n"
                f"• Try resetting the board\n"
                f"• Check if device is in flash mode (for ESP devices)")

    def _update_test_error(self, error_msg):
        """Update UI with test error"""
        self.test_button.config(state="normal", text="Test Connection")
        self.status_label.config(text="Connection test error ❌", foreground="red")
        self.log_message(f"❌ Connection test error: {error_msg}")
        messagebox.showerror("Connection Test Error", f"Error during connection test:\n{error_msg}")

def main():
    root = tk.Tk()
    app = JTechPixelUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
