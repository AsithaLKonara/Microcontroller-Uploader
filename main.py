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
                "command": "esptool.py",
                "args": ["--port", "{port}", "--baud", "{baud}", "write_flash", "0x00000", "{file}"],
                "description": "ESP8266 NodeMCU, Wemos D1 Mini"
            },
            "ESP32": {
                "command": "esptool.py",
                "args": ["--chip", "esp32", "--port", "{port}", "--baud", "{baud}", "write_flash", "0x1000", "{file}"],
                "description": "ESP32 DevKit, ESP32-WROOM"
            },
            "AVR": {
                "command": "avrdude",
                "args": ["-c", "arduino", "-p", "atmega328p", "-P", "{port}", "-b", "{baud}", "-U", "flash:w:{file}:i"],
                "description": "Arduino Uno, Nano, Pro Mini"
            },
            "STM32": {
                "command": "stm32flash",
                "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
                "description": "STM32F103, STM32F407"
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
        ttk.Button(main_frame, text="Browse", command=self.select_firmware_file).grid(row=1, column=2, pady=5)
        
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
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="About", command=self.show_about).grid(row=0, column=2, padx=10)
        
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
        filetypes = [
            ("Firmware files", "*.bin *.hex *.dat *.elf"),
            ("Binary files", "*.bin"),
            ("Hex files", "*.hex"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Firmware File", filetypes=filetypes)
        if filename:
            self.firmware_path.set(filename)
            self.log_message(f"Selected firmware: {os.path.basename(filename)}")
            
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
            desc = self.device_configs[device]["description"]
            self.device_desc_label.config(text=desc)
            self.log_message(f"Selected device: {device} - {desc}")
            
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
            
            if device in self.device_configs:
                config = self.device_configs[device]
                command = config["command"]
                args = [arg.format(port=port, baud=baud, file=firmware) for arg in config["args"]]
                
                self.log_message(f"Executing: {command} {' '.join(args)}")
                
                # Run the upload command
                process = subprocess.Popen([command] + args, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True,
                                         bufsize=1)
                
                # Monitor output
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.log_message(output.strip())
                        # Update progress based on output
                        if "Writing" in output and "%" in output:
                            try:
                                percent = int(output.split("%")[0].split()[-1])
                                self.upload_progress.set(percent)
                            except:
                                pass
                
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
• Real-time upload progress
• Detailed logging

Built with Python and Tkinter
© 2024 J Tech Pixel"""
        
        messagebox.showinfo("About J Tech Pixel Uploader", about_text)

def main():
    root = tk.Tk()
    app = JTechPixelUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
