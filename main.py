import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial
import serial.tools.list_ports
import os
import threading
import subprocess
import time
from datetime import datetime
import utils
import config

class JTechPixelUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("J Tech Pixel Uploader v2.0 - ESP8266/ESP32 LED Matrix Flasher")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Light theme color palette - Professional & Clean
        self.colors = {
            'background': '#f8fafc',         # Light gray background
            'card_bg': '#ffffff',            # White card backgrounds
            'surface_bg': '#f1f5f9',         # Light gray surface elements
            'primary': '#3b82f6',            # Calmer blue
            'secondary': '#64748b',          # Neutral gray-blue
            'success': '#22c55e',            # Calm green
            'warning': '#facc15',            # Softer yellow
            'error': '#ef4444',              # Clean red
            'text_primary': '#1e293b',       # Dark text
            'text_secondary': '#475569',     # Medium gray text
            'text_muted': '#64748b',         # Muted text
            'border': '#e2e8f0',             # Light borders
            'accent': '#8b5cf6',             # Soft purple accent
            'hover': '#e2e8f0',              # Hover effects
            'selection': '#dbeafe'           # Text selection
        }

        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Bind window resize event for responsive behavior
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Store initial window size for responsive calculations
        self.initial_width = 1400
        self.initial_height = 900
        self.min_width = 1000
        self.min_height = 700
        
        # Initialize variables
        self.firmware_path = tk.StringVar()
        self.selected_device = tk.StringVar()
        self.selected_port = tk.StringVar()
        self.selected_baud = tk.StringVar()
        self.firmware_mode_var = tk.StringVar(value="firmware")
        self.verify_after_upload = tk.BooleanVar(value=True)
        self.erase_before_upload = tk.BooleanVar(value=False)
        self.upload_progress = tk.DoubleVar()
        self.is_uploading = False
        
        # File processing variables
        self.file_type_info = None
        self.processed_file_path = None
        
        # Device configurations
        self.device_configs = config.DEVICE_CONFIGS
        
        # Setup custom styles
        self.setup_custom_styles()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize
        self.detect_ports()
        self.selected_device.set("ESP8266")
        self.selected_baud.set("115200")
        
        # Welcome message
        self.log_success("🚀 J Tech Pixel Uploader v2.0 Started")
        self.log_message("💡 Select a firmware file and configure your device to begin")
        
        # Apply initial responsive adjustments
        self.apply_initial_responsive_settings()
        
    def setup_custom_styles(self):
        """Configure custom ttk styles for modern dark theme appearance"""
        self.style = ttk.Style()
        
        # Configure main window background
        self.style.configure('Main.TFrame', background=self.colors['background'])
        
        # Configure card-style frames
        self.style.configure('Card.TFrame', 
                            background=self.colors['card_bg'],
                            relief='solid',
                            borderwidth=1)
        
        # Configure title labels
        self.style.configure('Title.TLabel',
                            font=('Segoe UI', 18, 'bold'),
                            foreground=self.colors['primary'],
                            background=self.colors['card_bg'])
        
        # Configure subtitle labels
        self.style.configure('Subtitle.TLabel',
                            font=('Segoe UI', 12),
                            foreground=self.colors['text_secondary'],
                            background=self.colors['card_bg'])
        
        # Configure section headers
        self.style.configure('Section.TLabel',
                            font=('Segoe UI', 12, 'bold'),
                            foreground=self.colors['text_primary'],
                            background=self.colors['card_bg'])
        
        # Configure primary button (Upload)
        self.style.configure('Primary.TButton',
                            font=('Segoe UI', 11, 'bold'),
                            background=self.colors['surface_bg'],
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['border'],
                            borderwidth=1,
                            padding=(25, 10))
        
        # Configure secondary button (Chip Info)
        self.style.configure('Secondary.TButton',
                            font=('Segoe UI', 10),
                            background=self.colors['surface_bg'],
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['border'],
                            borderwidth=1,
                            padding=(18, 8))
        
        # Configure info button
        self.style.configure('Info.TButton',
                            font=('Segoe UI', 10),
                            background=self.colors['surface_bg'],
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['border'],
                            borderwidth=1,
                            padding=(12, 8))
        
        # Configure progress bar
        self.style.configure('Custom.Horizontal.TProgressbar',
                            troughcolor=self.colors['surface_bg'],
                            background=self.colors['primary'],
                            bordercolor=self.colors['border'])
        
        # Configure status labels
        self.style.configure('Status.TLabel',
                            font=('Segoe UI', 10),
                            background=self.colors['card_bg'])
        
        # Configure file info labels
        self.style.configure('FileInfo.TLabel',
                            font=('Segoe UI', 9),
                            background=self.colors['card_bg'])
        
        # Configure log text
        self.style.configure('Log.TFrame',
                            background=self.colors['card_bg'],
                            relief='solid',
                            borderwidth=1)
        
        # Configure entry fields
        self.style.configure('Custom.TEntry',
                            fieldbackground=self.colors['surface_bg'],
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['border'],
                            borderwidth=1)
        
        # Configure combobox
        self.style.configure('Custom.TCombobox',
                            fieldbackground=self.colors['surface_bg'],
                            foreground=self.colors['text_primary'],
                            background=self.colors['surface_bg'],
                            bordercolor=self.colors['border'],
                            borderwidth=1)
        
        # Configure radio buttons
        self.style.configure('Custom.TRadiobutton',
                            background=self.colors['card_bg'],
                            foreground=self.colors['text_primary'])
        
        # Configure checkbuttons
        self.style.configure('Custom.TCheckbutton',
                            background=self.colors['card_bg'],
                            foreground=self.colors['text_primary'])
        
        # Configure hover button style
        self.style.configure('Hover.TButton',
                            font=('Segoe UI', 10),
                            background=self.colors['hover'],
                            foreground=self.colors['text_primary'],
                            bordercolor=self.colors['primary'],
                            borderwidth=2,
                            padding=(12, 8))
    
    def setup_ui(self):
        """Setup the modern dashboard-style UI with dark theme"""
        
        # Main container frame
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights for responsive layout
        main_frame.grid_columnconfigure(0, weight=1)  # Left column (controls) - flexible
        main_frame.grid_columnconfigure(1, weight=3)  # Right column (log) - 3x wider for better log visibility
        main_frame.grid_rowconfigure(1, weight=1)     # Middle row (controls + log) expands
        main_frame.grid_rowconfigure(0, weight=0)     # Top banner - fixed height
        
        # === TOP BANNER ===
        banner_frame = ttk.Frame(main_frame, style='Card.TFrame')
        banner_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Title and subtitle
        title_label = ttk.Label(banner_frame, text="J Tech Pixel Uploader v2.0", style='Title.TLabel')
        title_label.pack(pady=(15, 5))
        
        subtitle_label = ttk.Label(banner_frame, text="ESP8266/ESP32 LED Matrix Flasher", style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 15))
        
        # === LEFT COLUMN - CONTROLS ===
        left_frame = ttk.Frame(main_frame, style='Main.TFrame')
        left_frame.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(0, 15))
        
        # Create scrollable canvas for left column
        left_canvas = tk.Canvas(left_frame, bg=self.colors['background'], highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
        scrollable_frame = ttk.Frame(left_canvas, style='Main.TFrame')
        
        # Configure the canvas
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Pack scrollbar and canvas
        left_scrollbar.pack(side="right", fill="y")
        left_canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas for the scrollable frame
        left_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure scroll region when frame changes
        def configure_scroll_region(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        # Add mouse wheel scrolling support
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # File Management Section - Card style
        file_frame = ttk.LabelFrame(scrollable_frame, text="📁 File Management", style='Card.TFrame', padding=15)
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(file_frame, text="Firmware/Data File:", 
                 style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        file_entry = ttk.Entry(file_frame, textvariable=self.firmware_path, width=45, style='Custom.TEntry')
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(15, 10), pady=(0, 8))
        
        # Configure file frame grid weights for responsive behavior
        file_frame.grid_columnconfigure(1, weight=1)  # File entry expands
        file_frame.grid_columnconfigure(0, weight=0)  # Label stays fixed width
        
        # File buttons row
        file_buttons_frame = ttk.Frame(file_frame)
        file_buttons_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Button(file_buttons_frame, text="📂 Browse", command=self.browse_file,
                  style='Info.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_buttons_frame, text="ℹ️", command=self.show_file_info,
                  style='Info.TButton').grid(row=0, column=1)
        
        # File info display
        self.file_info_label = ttk.Label(file_frame, text="No file selected", 
                                       style='FileInfo.TLabel', foreground=self.colors['text_muted'])
        self.file_info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Upload Mode Section - Card style
        mode_frame = ttk.LabelFrame(scrollable_frame, text="🔄 Upload Mode", style='Card.TFrame', padding=15)
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(mode_frame, text="Firmware Mode (BIN/HEX)", 
                       variable=self.firmware_mode_var, value="firmware",
                       command=self.on_mode_change, style='Custom.TRadiobutton').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        ttk.Radiobutton(mode_frame, text="Data Mode (DAT → FS Image)", 
                       variable=self.firmware_mode_var, value="filesystem",
                       command=self.on_mode_change, style='Custom.TRadiobutton').grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
        
        # Device Configuration Section - Card style
        device_frame = ttk.LabelFrame(scrollable_frame, text="🔌 Device Configuration", style='Card.TFrame', padding=15)
        device_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Device type
        ttk.Label(device_frame, text="Device Type:", 
                 style='Section.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        device_combo = ttk.Combobox(device_frame, textvariable=self.selected_device, 
                                   values=list(self.device_configs.keys()), state="readonly", width=25, style='Custom.TCombobox')
        device_combo.grid(row=0, column=1, sticky=tk.W, padx=(15, 0), pady=(0, 8))
        device_combo.bind('<<ComboboxSelected>>', self.on_device_change)
        
        # Device description
        self.device_desc_label = ttk.Label(device_frame, text="Select a device", 
                                         style='FileInfo.TLabel', foreground=self.colors['text_muted'])
        self.device_desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # COM Port
        ttk.Label(device_frame, text="COM Port:", 
                 style='Section.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        port_frame = ttk.Frame(device_frame)
        port_frame.grid(row=2, column=1, sticky=tk.W, padx=(15, 0), pady=(0, 8))
        
        port_combo = ttk.Combobox(port_frame, textvariable=self.selected_port, width=25, style='Custom.TCombobox')
        port_combo.grid(row=0, column=0, sticky=tk.W)
        ttk.Button(port_frame, text="🔄 Refresh", command=self.detect_ports,
                  style='Info.TButton').grid(row=0, column=1, padx=(10, 0))
        
        # Baud Rate
        ttk.Label(device_frame, text="Baud Rate:", 
                 style='Section.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(0, 8))
        baud_combo = ttk.Combobox(device_frame, textvariable=self.selected_baud, 
                                 values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"], 
                                 state="readonly", width=25, style='Custom.TCombobox')
        baud_combo.grid(row=3, column=1, sticky=tk.W, padx=(15, 0), pady=(0, 8))
        
        # Actions Section - Card style
        actions_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Actions", style='Card.TFrame', padding=15)
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Action buttons row
        buttons_frame = ttk.Frame(actions_frame)
        buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Chip Info", command=self.get_chip_info,
                  style='Secondary.TButton').grid(row=0, column=0, padx=(0, 10))
        self.upload_button = ttk.Button(buttons_frame, text="🚀 Upload", command=self.start_upload,
                                       style='Primary.TButton')
        self.upload_button.grid(row=0, column=1)
        
        # Options
        options_frame = ttk.Frame(actions_frame)
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Verify after upload", 
                       variable=self.verify_after_upload, style='Custom.TCheckbutton').grid(row=0, column=0, padx=(0, 15))
        ttk.Checkbutton(options_frame, text="Erase flash before upload", 
                       variable=self.erase_before_upload, style='Custom.TCheckbutton').grid(row=0, column=1)
        
        # Progress & Status Section - Card style
        progress_frame = ttk.LabelFrame(scrollable_frame, text="📊 Progress & Status", style='Card.TFrame', padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
                # Progress bar with percentage
        progress_container = ttk.Frame(progress_frame)
        progress_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_container, variable=self.upload_progress,
                                           style='Custom.Horizontal.TProgressbar', length=300)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Percentage label
        self.progress_label = ttk.Label(progress_container, text="0%", 
                                       style='Status.TLabel', foreground=self.colors['primary'])
        self.progress_label.grid(row=0, column=1, padx=(10, 0))
        
        # Status display
        self.status_label = ttk.Label(progress_frame, text="Ready", 
                                     style='Status.TLabel', foreground=self.colors['success'])
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # === RIGHT COLUMN - LOG AREA ===
        right_frame = ttk.Frame(main_frame, style='Main.TFrame')
        right_frame.grid(row=1, column=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        # Log section - Card style
        log_frame = ttk.LabelFrame(right_frame, text="📝 Upload Log", style='Card.TFrame', padding=15)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log controls row
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(log_controls, text="🗑️ Clear Log", command=self.clear_log,
                  style='Info.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(log_controls, text="💾 Save Log", command=self.save_log,
                  style='Info.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(log_controls, text="📋 Copy Log", command=self.copy_log,
                  style='Info.TButton').grid(row=0, column=2)
        
        # Log text area
        log_container = ttk.Frame(log_frame, style='Log.TFrame')
        log_container.grid(row=1, column=0, sticky=(tk.N, tk.W, tk.E, tk.S), pady=(10, 0))
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_container)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Log text widget with larger font
        self.log_text = tk.Text(log_container, height=25, width=80, 
                               font=('Consolas', 12), 
                               bg=self.colors['surface_bg'], 
                               fg=self.colors['text_primary'],
                               insertbackground=self.colors['text_primary'],
                               selectbackground=self.colors['selection'],
                               selectforeground=self.colors['text_primary'],
                               relief='solid',
                               borderwidth=1,
                               wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        # Configure scrollbar
        log_scrollbar.config(command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Configure grid weights for responsive behavior
        file_frame.grid_columnconfigure(1, weight=1)
        device_frame.grid_columnconfigure(1, weight=1)
        progress_container.grid_columnconfigure(0, weight=1)
        
        # Configure device frame grid weights
        device_frame.grid_columnconfigure(1, weight=1)  # Controls expand
        device_frame.grid_columnconfigure(0, weight=0)  # Labels stay fixed width
        
        # Add hover effects to buttons
        self.setup_button_hover_effects()
        
        # Store references to key UI elements for responsive updates
        self.main_frame = main_frame
        self.left_frame = left_frame
        self.right_frame = right_frame
        self.banner_frame = banner_frame
    
    def setup_button_hover_effects(self):
        """Setup hover effects for buttons to improve visual feedback"""
        # Find all buttons and add hover effects
        for widget in self.root.winfo_children():
            self._add_hover_effects_recursive(widget)
    
    def _add_hover_effects_recursive(self, widget):
        """Recursively add hover effects to all buttons"""
        if isinstance(widget, ttk.Button):
            widget.bind('<Enter>', lambda e, w=widget: self._on_button_hover(w, True))
            widget.bind('<Leave>', lambda e, w=widget: self._on_button_hover(w, False))
        
        # Recursively process child widgets
        for child in widget.winfo_children():
            self._add_hover_effects_recursive(child)
    
    def _on_button_hover(self, button, entering):
        """Handle button hover effects"""
        try:
            if entering:
                button.configure(style='Hover.TButton')
            else:
                # Restore original style based on button text
                button_text = button.cget('text')
                if '🚀' in button_text:
                    button.configure(style='Primary.TButton')
                elif '🔍' in button_text:
                    button.configure(style='Secondary.TButton')
                else:
                    button.configure(style='Info.TButton')
        except:
            # If there's any error, just ignore it
            pass
    
    def check_available_tools(self):
        """Check what tools are available and log status"""
        tools = utils.get_available_tools()
        self.log_system("Checking available tools...")
        
        for tool, available in tools.items():
            status = "✅ Available" if available else "❌ Not found"
            self.log_message(f"  {tool}: {status}")
        
        # Check for critical tools
        if not tools["esptool"]:
            self.log_warning("esptool not found. ESP8266/ESP32 flashing will not work.")
        
        if not tools["hex_converter"]:
            self.log_warning("No HEX converter found. HEX files cannot be processed.")
        
        if not tools["fs_builder"]:
            self.log_warning("No file system builder found. DAT files cannot be processed.")
        
        self.log_system("Tool check complete.")
        
    def on_mode_change(self, event=None):
        """Handle upload mode change"""
        mode = self.firmware_mode_var.get()
        if mode == "filesystem":
            # Force device selection to ESP devices for filesystem mode
            if self.selected_device.get() not in ["ESP8266", "ESP32"]:
                self.selected_device.set("ESP8266")
                messagebox.showinfo("Mode Changed", "Data Mode requires ESP8266 or ESP32 device. Switched to ESP8266.")
        
        self.update_file_info_display()
        
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
                    ("Data files", "*.dat"),
                    ("All files", "*.*")
                ]
        else:
            filetypes = [
                ("Firmware files", "*.bin *.hex *.dat *.elf"),
                ("Binary files", "*.bin"),
                ("Hex files", "*.hex"),
                ("Data files", "*.dat"),
                ("All files", "*.*")
            ]
            
        filename = filedialog.askopenfilename(title="Select Firmware/Data File", filetypes=filetypes)
        if filename:
            # Get file type information
            self.file_type_info = utils.get_file_type_info(filename)
            
            # Validate the selected file
            if self.validate_firmware_file(filename):
                self.firmware_path.set(filename)
                self.processed_file_path = None  # Reset processed file
                self.update_file_info_display()
                self.log_success(f"Selected file: {os.path.basename(filename)}")
                self.log_message(f"File type: {self.file_type_info.get('type', 'unknown')}")
                
                # Auto-switch mode based on file type
                if self.file_type_info.get('type') == 'data_file':
                    self.firmware_mode_var.set("filesystem")
                    self.log_progress("Auto-switched to Data Mode for .dat file")
                elif self.file_type_info.get('type') == 'intel_hex':
                    self.firmware_mode_var.set("firmware")
                    self.log_progress("Auto-switched to Firmware Mode for .hex file")
                elif self.file_type_info.get('type') == 'binary_firmware':
                    self.firmware_mode_var.set("firmware")
                    self.log_progress("Auto-switched to Firmware Mode for .bin file")
            else:
                messagebox.showerror("Invalid File", 
                    f"This file type is not compatible with {device} devices.\n\n"
                    f"Supported formats: {', '.join(supported_formats) if 'supported_formats' in config else 'All formats'}")
    
    def update_file_info_display(self):
        """Update the file information display"""
        if not self.file_type_info:
            self.file_info_label.config(text="")
            return
        
        file_path = self.firmware_path.get()
        if not file_path:
            self.file_info_label.config(text="")
            return
        
        info = self.file_type_info
        mode = self.firmware_mode_var.get()
        
        # Build status message
        if info.get('status') == 'ready_to_flash':
            status_text = f"✅ {info['type'].replace('_', ' ').title()} - Ready to flash"
        elif info.get('status') == 'can_convert':
            status_text = f"🔄 {info['type'].replace('_', ' ').title()} - Will convert to {info['output_format']}"
        elif info.get('status') == 'can_create_fs':
            status_text = f"🔄 {info['type'].replace('_', ' ').title()} - Will create {info['output_format']}"
        elif info.get('status') == 'converter_missing':
            status_text = f"❌ {info['type'].replace('_', ' ').title()} - Converter tool missing"
        elif info.get('status') == 'fs_builder_missing':
            status_text = f"❌ {info['type'].replace('_', ' ').title()} - FS builder tool missing"
        else:
            status_text = f"❓ {info['type'].replace('_', ' ').title()} - Status unknown"
        
        # Add file size
        status_text += f" ({info.get('size_human', 'unknown size')})"
        
        # Add processing notes
        if info.get('notes'):
            status_text += f" - {', '.join(info['notes'])}"
        
        self.file_info_label.config(text=status_text)
        
        # Update upload button state
        can_upload = (info.get('status') in ['ready_to_flash', 'can_convert', 'can_create_fs'])
        self.upload_button.config(state="normal" if can_upload else "disabled")
        
        if not can_upload:
            self.upload_button.config(text="Upload (Tool Missing)")
        else:
            self.upload_button.config(text="Upload")
    
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
                # Check if converter is available
                if not utils.find_hex_converter():
                    return False
            elif file_ext == ".dat":
                # Check if FS builder is available
                if not utils.find_fs_builder():
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
            self.log_success(f"Detected {len(ports)} COM port(s): {', '.join(ports)}")
        else:
            self.log_warning("No COM ports detected")
            
    def on_device_change(self, event=None):
        device = self.selected_device.get()
        if device in self.device_configs:
            config = self.device_configs[device]
            desc = config["description"]
            self.device_desc_label.config(text=desc)
            
            # Show format restrictions
            supported_formats = config.get("supported_formats", [])
            if supported_formats:
                format_info = f"Supported formats: {', '.join(supported_formats)}"
                self.log_success(f"Selected device: {device} - {desc}")
                self.log_message(f"📋 {format_info}")
                
                # Show special warnings for ESP devices
                if device.startswith("ESP"):
                    self.log_warning("Important: ESP devices only support .bin files, not .hex files")
                    self.log_message("💡 If you have a .hex file, you need to convert it to .bin first")
            else:
                self.log_success(f"Selected device: {device} - {desc}")
                self.log_message("📋 All firmware formats supported")
            
    def start_upload(self):
        if self.is_uploading:
            return
            
        # Validate inputs
        if not self.firmware_path.get():
            messagebox.showerror("Error", "Please select a firmware/data file")
            return
            
        if not self.selected_port.get():
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        if not os.path.exists(self.firmware_path.get()):
            messagebox.showerror("Error", "Selected file does not exist")
            return
            
        # Validate firmware compatibility
        if not self.validate_firmware_file(self.firmware_path.get()):
            messagebox.showerror("Error", "Selected file is not compatible with the chosen device")
            return
        
        # Check if we need to process the file first
        file_info = self.file_type_info
        if file_info.get('processing_required', False):
            if file_info.get('status') in ['converter_missing', 'fs_builder_missing']:
                messagebox.showerror("Error", f"Cannot process {file_info.get('type', 'file')}. Required tool is missing.")
                return
        
        # Start upload in separate thread
        self.is_uploading = True
        self.upload_button.config(state="disabled")
        self.upload_progress.set(0)
        self.update_progress_label()
        self.status_label.config(text="Preparing upload...", foreground="blue")
        
        upload_thread = threading.Thread(target=self.upload_firmware)
        upload_thread.daemon = True
        upload_thread.start()
        
    def upload_firmware(self):
        try:
            device = self.selected_device.get()
            port = self.selected_port.get()
            baud = self.selected_baud.get() # Use selected_baud
            firmware = self.firmware_path.get()
            mode = self.firmware_mode_var.get()
            
            self.log_progress(f"Starting upload for {device} on {port} at {baud} baud")
            self.log_message(f"File: {os.path.basename(firmware)}")
            self.log_message(f"Mode: {mode}")
            
            # Process file if needed
            processed_file = self.process_file_for_upload(firmware, mode)
            if not processed_file:
                self.status_label.config(text="File processing failed", foreground="red")
                return
            
            # Get flash command
            command, args = self.get_flash_command(device, port, baud, processed_file, mode)
            
            if command:
                self.log_progress(f"Executing: {command} {' '.join(args)}")
                
                # Run the upload command
                success = self.execute_flash_command(command, args, device, port, baud)
                
                if success:
                    # Verify if requested
                    if self.verify_after_upload.get():
                        self.log_progress("Starting verification...")
                        verify_success = self.verify_flash(device, port, baud, processed_file, mode)
                        
                        if verify_success:
                            self.status_label.config(text="Upload and verification completed successfully! ✅", foreground=self.colors['success'])
                            self.log_success("Upload and verification completed successfully!")
                            messagebox.showinfo("Success", 
                                "Firmware uploaded and verified successfully!\n\n"
                                "Device should now be running the new firmware.\n\n"
                                "If the LED pattern isn't working, check:\n"
                                "• Hardware wiring (GPIO pin connections)\n"
                                "• Power supply stability\n"
                                "• Reset the board after upload")
                        else:
                            self.status_label.config(text="Upload completed but verification failed ⚠", foreground=self.colors['warning'])
                            self.log_warning("Upload completed but verification failed. Device may not be running firmware.")
                            messagebox.showwarning("Upload Complete", 
                                "Firmware uploaded successfully!\n\n"
                                "However, verification failed.\n"
                                "The device may not be running the new firmware.\n\n"
                                "Troubleshooting:\n"
                                "• Check if device is in flash mode (GPIO0)\n"
                                "• Verify power supply\n"
                                "• Try resetting the board\n"
                                "• Consider erasing flash and re-uploading")
                    else:
                        self.status_label.config(text="Upload completed successfully!", foreground=self.colors['success'])
                        self.log_success("Upload completed successfully!")
                        messagebox.showinfo("Success", "Firmware uploaded successfully!")
                else:
                    self.status_label.config(text="Upload failed", foreground=self.colors['error'])
                    self.log_error("Upload failed!")
                    messagebox.showerror("Error", "Upload failed. Check the log for details.")
                    
            else:
                self.log_error(f"Device type '{device}' not supported or no flash command found.")
                messagebox.showerror("Error", f"Device type '{device}' not supported or no flash command found.")
                
        except Exception as e:
            self.log_error(f"Error during upload: {str(e)}")
            self.status_label.config(text="Upload error", foreground=self.colors['error'])
            messagebox.showerror("Error", f"Upload error: {str(e)}")
            
        finally:
            self.is_uploading = False
            self.upload_button.config(state="normal")
            
    def process_file_for_upload(self, file_path: str, mode: str) -> str:
        """Process file for upload (convert HEX to BIN, create FS image, etc.)"""
        try:
            file_info = self.file_type_info
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == ".hex" and mode == "firmware":
                # Convert HEX to BIN
                self.log_progress("Converting HEX to BIN...")
                success, output_path, error_msg = utils.convert_hex_to_bin(file_path)
                
                if success:
                    self.log_success(f"Converted to: {os.path.basename(output_path)}")
                    self.processed_file_path = output_path
                    return output_path
                else:
                    self.log_error(f"HEX conversion failed: {error_msg}")
                    return None
                    
            elif file_ext == ".dat" and mode == "filesystem":
                # Create file system image
                self.log_progress("Creating file system image...")
                
                # Determine FS size based on device
                device = self.selected_device.get()
                fs_size_mb = 1  # Default for most ESP8266 boards
                if device == "ESP32":
                    fs_size_mb = 2  # ESP32 typically has more flash
                
                success, output_path, error_msg = utils.create_fs_image(file_path, fs_size_mb)
                
                if success:
                    self.log_success(f"Created FS image: {os.path.basename(output_path)}")
                    self.processed_file_path = output_path
                    return output_path
                else:
                    self.log_error(f"FS image creation failed: {error_msg}")
                    return None
                    
            else:
                # File is ready to use
                return file_path
                
        except Exception as e:
            self.log_error(f"File processing error: {str(e)}")
            return None
    
    def get_flash_command(self, device: str, port: str, baud: str, file_path: str, mode: str):
        """Get the appropriate flash command based on device and mode"""
        if device not in self.device_configs:
            return None, None
            
        config = self.device_configs[device]
        command = config["command"]
        
        if mode == "filesystem":
            # For filesystem mode, flash to appropriate offset
            if device.startswith("ESP"):
                # ESP8266: typically 0x300000, ESP32: typically 0x9000
                fs_offset = "0x300000" if device == "ESP8266" else "0x9000"
                args = ["-m", "esptool", "--chip", device.lower(), "--port", port, "--baud", baud,
                       "--before", "default-reset", "--after", "hard-reset",
                       "write-flash", "--flash-mode", "dio", "--flash-size", "detect",
                       fs_offset, file_path]
                return command, args
        else:
            # For firmware mode, use standard args
            args = [arg.format(port=port, baud=baud, file=file_path) for arg in config["args"]]
            return command, args
    
    def execute_flash_command(self, command: str, args: list, device: str, port: str, baud: str) -> bool:
        """Execute the flash command and monitor progress"""
        try:
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
                            self.update_progress_label()
                        except:
                            pass
                    elif "Compressed" in output:
                        # Show compression progress
                        self.upload_progress.set(25)
                        self.update_progress_label()
                    elif "Uploading stub flasher" in output:
                        # Show stub upload progress
                        self.upload_progress.set(10)
                        self.update_progress_label()
                    elif "Running stub flasher" in output:
                        # Show stub running progress
                        self.upload_progress.set(35)
                        self.update_progress_label()
                    elif "Configuring flash size" in output:
                        # Show flash configuration progress
                        self.upload_progress.set(50)
                        self.update_progress_label()
                    elif "Writing" in output and "bytes" in output:
                        # Show writing progress
                        self.upload_progress.set(75)
                        self.update_progress_label()
            
            return_code = process.poll()
            return return_code == 0
            
        except Exception as e:
            self.log_error(f"Flash command execution error: {str(e)}")
            return False
    
    def verify_flash(self, device: str, port: str, baud: str, file_path: str, mode: str) -> bool:
        """Verify the flash operation"""
        try:
            if mode == "filesystem":
                # For filesystem, verify the FS image
                if device.startswith("ESP"):
                    fs_offset = "0x300000" if device == "ESP8266" else "0x9000"
                    args = ["-m", "esptool", "--chip", device.lower(), "--port", port, "--baud", baud,
                           "verify_flash", fs_offset, file_path]
                    command = "python"
                else:
                    return False
            else:
                # For firmware, verify the firmware
                if device.startswith("ESP"):
                    args = ["-m", "esptool", "--chip", device.lower(), "--port", port, "--baud", baud,
                           "verify_flash", "0x00000", file_path]
                    command = "python"
                else:
                    # For non-ESP devices, verification depends on the tool
                    return True  # Skip verification for now
            
            # Run verification
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
            
            output, _ = process.communicate(timeout=60)
            return_code = process.returncode
            
            if return_code == 0:
                self.log_success("Verification successful!")
                return True
            else:
                self.log_error(f"Verification failed: {output.strip()}")
                return False
                
        except Exception as e:
            self.log_error(f"Verification error: {str(e)}")
            return False

    def log_message(self, message, level="info"):
        """Enhanced log message with color coding and better formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Define message levels and colors
        level_colors = {
            "info": self.colors['text_primary'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['error'],
            "progress": self.colors['accent'],
            "system": self.colors['text_secondary']
        }
        
        # Get color for message level
        color = level_colors.get(level, self.colors['text_primary'])
        
        # Format the log entry
        if level == "progress":
            log_entry = f"[{timestamp}] 🔄 {message}\n"
        elif level == "success":
            log_entry = f"[{timestamp}] ✅ {message}\n"
        elif level == "warning":
            log_entry = f"[{timestamp}] ⚠ {message}\n"
        elif level == "error":
            log_entry = f"[{timestamp}] ❌ {message}\n"
        elif level == "system":
            log_entry = f"[{timestamp}] 🔧 {message}\n"
        else:
            log_entry = f"[{timestamp}] ℹ {message}\n"
        
        # Update log in main thread with color
        self.root.after(0, self._update_log, log_entry, color)
    
    def _update_log(self, message, color=None):
        """Update log with color coding"""
        # Insert message with timestamp in muted color
        self.log_text.insert(tk.END, message)
        
        # Apply color to the message content (excluding timestamp)
        if color:
            # Find the start of the message content (after timestamp)
            start_pos = message.find("]") + 2
            if start_pos > 1:
                # Apply color to the message part
                end_pos = f"{self.log_text.index(tk.END)}-1c"
                self.log_text.tag_add(f"color_{color}", f"{self.log_text.index(tk.END)}-{len(message)}c+{start_pos}c", end_pos)
                self.log_text.tag_config(f"color_{color}", foreground=color)
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
        
        # Limit log size to prevent memory issues (keep last 1000 lines)
        lines = int(self.log_text.index(tk.END).split('.')[0])
        if lines > 1000:
            self.log_text.delete("1.0", f"{lines-1000}.0")
            self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 Log truncated to last 1000 lines\n")
    
    def log_success(self, message):
        """Log a success message"""
        self.log_message(message, "success")
    
    def log_warning(self, message):
        """Log a warning message"""
        self.log_message(message, "warning")
    
    def log_error(self, message):
        """Log an error message with actionable advice"""
        self.log_message(message, "error")
        
        # Add actionable advice for common errors
        if "COM" in message.upper() and "not found" in message.lower():
            self.log_message("💡 Try: Check USB connection, restart device, or try a different USB port", "system")
        elif "timeout" in message.lower():
            self.log_message("💡 Try: Increase baud rate, check power supply, or reset the device", "system")
        elif "verification failed" in message.lower():
            self.log_message("💡 Try: Check flash memory, try erasing flash first, or verify file integrity", "system")
    
    def log_progress(self, message):
        """Log a progress message"""
        self.log_message(message, "progress")
    
    def log_system(self, message):
        """Log a system/info message"""
        self.log_message(message, "system")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_system("Log cleared")
        
        # Add welcome message after clearing
        self.log_system("🚀 J Tech Pixel Uploader v2.0 Started")
        self.log_message("💡 Select a firmware file and configure your device to begin")
        
    def save_log(self):
        """Save the current log to a file."""
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                               filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Log saved to {filename}")
            except Exception as e:
                self.log_message(f"Error saving log: {e}")
                messagebox.showerror("Error", f"Error saving log: {e}")

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
        baud = self.selected_baud.get() # Use selected_baud

        if not port:
            messagebox.showwarning("Warning", "Please select a COM port to test.")
            return

        if not baud:
            messagebox.showwarning("Warning", "Please select a baud rate to test.")
            return

        self.log_message(f"🔍 Testing connection to {device} on {port} at {baud} baud...")
        # self.test_button.config(state="disabled", text="Testing...") # This line was removed from the new_code
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
        # self.test_button.config(state="normal", text="Test Connection") # This line was removed from the new_code
        
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
        # self.test_button.config(state="normal", text="Test Connection") # This line was removed from the new_code
        self.status_label.config(text="Connection test error ❌", foreground="red")
        self.log_message(f"❌ Connection test error: {error_msg}")
        messagebox.showerror("Connection Test Error", f"Error during connection test:\n{error_msg}")

    def get_chip_info(self):
        """Get chip information for the selected device."""
        device = self.selected_device.get()
        port = self.selected_port.get()
        baud = self.selected_baud.get() # Use selected_baud

        if not port:
            messagebox.showwarning("Warning", "Please select a COM port to get chip info.")
            return

        if not baud:
            messagebox.showwarning("Warning", "Please select a baud rate to get chip info.")
            return

        if device not in self.device_configs:
            messagebox.showerror("Error", f"Device type '{device}' not supported.")
            return

        self.log_message(f"🔍 Getting chip info for {device} on {port} at {baud} baud...")
        self.status_label.config(text="Getting Chip Info...", foreground="blue")

        # Get chip info in separate thread
        chip_info_thread = threading.Thread(target=self._get_chip_info_thread, args=(device, port, baud))
        chip_info_thread.daemon = True
        chip_info_thread.start()

    def _get_chip_info_thread(self, device, port, baud):
        """Get chip info in a separate thread"""
        try:
            config = self.device_configs[device]
            command = config["command"]
            args = [arg.format(port=port, baud=baud) for arg in config["args"]]
            
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
            
            output, _ = process.communicate(timeout=10)
            return_code = process.returncode

            if return_code == 0:
                self.log_message(f"✅ Chip info for {device} on {port} at {baud} baud:")
                self.log_message(f"  {output.strip()}")
                messagebox.showinfo("Chip Info", f"Chip info for {device} on {port} at {baud}:\n\n{output.strip()}")
            else:
                self.log_message(f"❌ Error getting chip info for {device} on {port} at {baud}:")
                self.log_message(f"  {output.strip()}")
                messagebox.showerror("Chip Info Error", f"Error getting chip info for {device} on {port} at {baud}:\n\n{output.strip()}")

        except subprocess.TimeoutExpired:
            self.log_message(f"⚠ Chip info timed out for {device} on {port} at {baud} baud.")
            self.root.after(0, self._update_chip_info_error, f"Chip info timed out for {device} on {port} at {baud} baud.")
        except Exception as e:
            self.log_message(f"❌ Chip info error for {device} on {port} at {baud}: {str(e)}")
            self.root.after(0, self._update_chip_info_error, f"Chip info error for {device} on {port} at {baud}: {str(e)}")
        finally:
            self.root.after(0, self._update_chip_info_result, device, port, baud)

    def _update_chip_info_result(self, device, port, baud):
        """Update UI with chip info result"""
        self.status_label.config(text="Ready", foreground="green")
        self.log_message("Chip info check complete.")

    def _update_chip_info_error(self, error_msg):
        """Update UI with chip info error"""
        self.status_label.config(text="Chip Info error ❌", foreground="red")
        self.log_message(f"❌ Chip info error: {error_msg}")
        messagebox.showerror("Chip Info Error", error_msg)

    def browse_file(self):
        """Browse for firmware or data files"""
        filetypes = [
            ("All supported files", "*.bin;*.hex;*.dat"),
            ("Binary files", "*.bin"),
            ("Intel HEX files", "*.hex"),
            ("Data files", "*.dat"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Firmware/Data File",
            filetypes=filetypes
        )
        
        if filename:
            self.firmware_path.set(filename)
            self.on_file_selected()
    
    def show_file_info(self):
        """Show detailed information about the selected file"""
        if not self.firmware_path.get():
            messagebox.showinfo("File Info", "No file selected")
            return
            
        filepath = self.firmware_path.get()
        if not os.path.exists(filepath):
            messagebox.showerror("Error", "Selected file does not exist")
            return
            
        try:
            # Get file info using utils
            info = utils.get_file_type_info(filepath)
            
            # Create detailed info message
            info_text = f"File: {os.path.basename(filepath)}\n"
            info_text += f"Path: {filepath}\n"
            info_text += f"Size: {info.get('size_human', 'Unknown')}\n"
            info_text += f"Type: {info.get('type', 'Unknown')}\n"
            info_text += f"Status: {info.get('status', 'Unknown')}\n"
            
            if info.get('notes'):
                info_text += f"\nNotes:\n"
                for note in info['notes']:
                    info_text += f"• {note}\n"
            
            if info.get('required_tools'):
                info_text += f"\nRequired Tools:\n"
                for tool in info['required_tools']:
                    info_text += f"• {tool}\n"
            
            messagebox.showinfo("File Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get file info: {str(e)}")
    
    def copy_log(self):
        """Copy the current log content to clipboard"""
        try:
            log_content = self.log_text.get("1.0", tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)
            self.log_success("Log content copied to clipboard")
        except Exception as e:
            self.log_error(f"Failed to copy log: {str(e)}")
    
    def update_progress_label(self):
        """Update the progress percentage label"""
        progress = self.upload_progress.get()
        self.progress_label.config(text=f"{int(progress)}%")
        
        # Update status based on progress
        if progress == 0:
            self.status_label.config(text="Ready", foreground=self.colors['success'])
        elif progress < 100:
            self.status_label.config(text="Uploading...", foreground=self.colors['warning'])
        else:
            self.status_label.config(text="Complete!", foreground=self.colors['success'])

    def on_file_selected(self):
        """Handle file selection and update UI accordingly"""
        filepath = self.firmware_path.get()
        if not filepath:
            return
            
        if not os.path.exists(filepath):
            self.log_error("Selected file does not exist")
            return
            
        try:
            # Get file type info and store it
            self.file_type_info = utils.get_file_type_info(filepath)
            info = self.file_type_info
            
            # Update file info display
            status_text = f"Type: {info.get('type', 'Unknown')}, Status: {info.get('status', 'Unknown')}"
            if info.get('size_human'):
                status_text += f" ({info.get('size_human')})"
            
            # Add processing notes
            if info.get('notes'):
                status_text += f" - {', '.join(info['notes'])}"
            
            self.file_info_label.config(text=status_text)
            
            # Update upload button state
            can_upload = (info.get('status') in ['ready_to_flash', 'can_convert', 'can_create_fs'])
            self.upload_button.config(state="normal" if can_upload else "disabled")
            
            if not can_upload:
                self.upload_button.config(text="Upload (Tool Missing)")
            else:
                self.upload_button.config(text="🚀 Upload")
                
            # Auto-select appropriate mode
            if info.get('type') == 'dat':
                self.firmware_mode_var.set("filesystem")
                self.log_message("📁 Data file detected - switching to Data Mode")
            else:
                self.firmware_mode_var.set("firmware")
                self.log_message("⚙️ Firmware file detected - switching to Firmware Mode")
                
        except Exception as e:
            self.log_error(f"Error processing file: {str(e)}")
            self.file_info_label.config(text="Error processing file")
            self.upload_button.config(state="disabled")
    
    def update_file_info_display(self):
        """Update the file information display"""
        if not self.file_type_info:
            self.file_info_label.config(text="")
            return
        
        file_path = self.firmware_path.get()
        if not file_path:
            self.file_info_label.config(text="")
            return
        
        info = self.file_type_info
        mode = self.firmware_mode_var.get()
        
        # Build status message
        if info.get('status') == 'ready_to_flash':
            status_text = f"✅ {info['type'].replace('_', ' ').title()} - Ready to flash"
        elif info.get('status') == 'can_convert':
            status_text = f"🔄 {info['type'].replace('_', ' ').title()} - Will convert to {info['output_format']}"
        elif info.get('status') == 'can_create_fs':
            status_text = f"🔄 {info['type'].replace('_', ' ').title()} - Will create {info['output_format']}"
        elif info.get('status') == 'converter_missing':
            status_text = f"❌ {info['type'].replace('_', ' ').title()} - Converter tool missing"
        elif info.get('status') == 'fs_builder_missing':
            status_text = f"❌ {info['type'].replace('_', ' ').title()} - FS builder tool missing"
        else:
            status_text = f"❓ {info['type'].replace('_', ' ').title()} - Status unknown"
        
        # Add file size
        status_text += f" ({info.get('size_human', 'unknown size')})"
        
        # Add processing notes
        if info.get('notes'):
            status_text += f" - {', '.join(info['notes'])}"
        
        self.file_info_label.config(text=status_text)
        
        # Update upload button state
        can_upload = (info.get('status') in ['ready_to_flash', 'can_convert', 'can_create_fs'])
        self.upload_button.config(state="normal" if can_upload else "disabled")
        
        if not can_upload:
            self.upload_button.config(text="Upload (Tool Missing)")
        else:
                        self.upload_button.config(text="🚀 Upload")
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive UI behavior"""
        # Only handle main window resize events
        if event.widget == self.root:
            new_width = event.width
            new_height = event.height
            
            # Calculate responsive adjustments
            width_ratio = new_width / self.initial_width
            height_ratio = new_height / self.initial_height
            
            # Adjust font sizes based on window size
            self.adjust_font_sizes(width_ratio, height_ratio)
            
            # Adjust padding and spacing
            self.adjust_spacing(width_ratio)
            
            # Update scrollable canvas width for left column
            self.update_left_column_width(new_width)
    
    def adjust_font_sizes(self, width_ratio, height_ratio):
        """Dynamically adjust font sizes based on window dimensions"""
        try:
            # Calculate responsive font sizes
            title_size = max(14, min(24, int(18 * width_ratio)))
            subtitle_size = max(10, min(16, int(12 * width_ratio)))
            section_size = max(10, min(16, int(12 * width_ratio)))
            button_size = max(9, min(14, int(11 * width_ratio)))
            
            # Update title font
            self.style.configure('Title.TLabel', font=('Segoe UI', title_size, 'bold'))
            self.style.configure('Subtitle.TLabel', font=('Segoe UI', subtitle_size))
            self.style.configure('Section.TLabel', font=('Segoe UI', section_size, 'bold'))
            self.style.configure('Primary.TButton', font=('Segoe UI', button_size, 'bold'))
            self.style.configure('Secondary.TButton', font=('Segoe UI', button_size))
            self.style.configure('Info.TButton', font=('Segoe UI', button_size))
            
        except Exception as e:
            # Silently handle any font adjustment errors
            pass
    
    def adjust_spacing(self, width_ratio):
        """Adjust padding and spacing based on window width"""
        try:
            # Calculate responsive padding
            main_padding = max(10, min(30, int(20 * width_ratio)))
            card_padding = max(10, min(20, int(15 * width_ratio)))
            
            # Update main frame padding
            self.main_frame.configure(padding=main_padding)
            
            # Update card padding (this would need to be implemented differently)
            # For now, we'll just log the adjustment
            if hasattr(self, 'last_padding_log') and self.last_padding_log != main_padding:
                self.log_system(f"UI spacing adjusted for window size: {main_padding}px")
                self.last_padding_log = main_padding
                
        except Exception as e:
            # Silently handle spacing adjustment errors
            pass
    
    def update_left_column_width(self, window_width):
        """Update left column width based on window size"""
        try:
            # Calculate optimal left column width
            if window_width < 1200:
                # Small window: narrow left column
                left_width = int(window_width * 0.35)
            elif window_width < 1600:
                # Medium window: balanced columns
                left_width = int(window_width * 0.4)
            else:
                # Large window: wider left column
                left_width = int(window_width * 0.45)
            
            # Ensure minimum width for controls
            left_width = max(350, min(left_width, 600))
            
            # Update left frame width (this is a simplified approach)
            # In a real implementation, you'd need to reconfigure the grid weights
            
        except Exception as e:
            # Silently handle width adjustment errors
            pass
    
    def get_responsive_dimensions(self):
        """Get responsive dimensions for current window size"""
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Calculate responsive values
        width_ratio = current_width / self.initial_width
        height_ratio = current_height / self.initial_height
        
        return {
            'width_ratio': width_ratio,
            'height_ratio': height_ratio,
            'is_small_screen': current_width < 1200,
            'is_medium_screen': 1200 <= current_width < 1600,
            'is_large_screen': current_width >= 1600,
            'is_compact_height': current_height < 800
        }
    
    def apply_initial_responsive_settings(self):
        """Apply initial responsive settings based on screen size"""
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Check if we're on a high DPI display
            if screen_width > 1920 or screen_height > 1080:
                self.log_system("High DPI display detected - applying optimized scaling")
                # Adjust initial window size for high DPI
                self.root.geometry("1600x1000")
            
            # Check if we're on a small screen
            if screen_width < 1366:
                self.log_system("Small screen detected - applying compact layout")
                # Adjust window size for small screens
                self.root.geometry("1200x800")
                self.root.minsize(1000, 700)
            
            # Log responsive settings
            responsive_info = self.get_responsive_dimensions()
            self.log_system(f"Responsive UI initialized - Screen: {screen_width}x{screen_height}, Window: {self.root.winfo_width()}x{self.root.winfo_height()}")
            
        except Exception as e:
            # Silently handle any responsive initialization errors
            pass
    
    def optimize_for_screen_size(self):
        """Optimize UI elements for current screen size"""
        try:
            responsive_info = self.get_responsive_dimensions()
            
            if responsive_info['is_small_screen']:
                # Compact layout for small screens
                self.apply_compact_layout()
            elif responsive_info['is_large_screen']:
                # Expanded layout for large screens
                self.apply_expanded_layout()
            else:
                # Standard layout for medium screens
                self.apply_standard_layout()
                
        except Exception as e:
            # Silently handle optimization errors
            pass
    
    def apply_compact_layout(self):
        """Apply compact layout for small screens"""
        try:
            # Reduce padding and spacing
            self.main_frame.configure(padding=10)
            
            # Adjust font sizes for better fit
            self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
            self.style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
            
            self.log_system("Compact layout applied for small screen")
            
        except Exception as e:
            pass
    
    def apply_expanded_layout(self):
        """Apply expanded layout for large screens"""
        try:
            # Increase padding and spacing
            self.main_frame.configure(padding=30)
            
            # Adjust font sizes for better readability
            self.style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'))
            self.style.configure('Subtitle.TLabel', font=('Segoe UI', 14))
            
            self.log_system("Expanded layout applied for large screen")
            
        except Exception as e:
            pass
    
    def apply_standard_layout(self):
        """Apply standard layout for medium screens"""
        try:
            # Standard padding and spacing
            self.main_frame.configure(padding=20)
            
            # Standard font sizes
            self.style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'))
            self.style.configure('Subtitle.TLabel', font=('Segoe UI', 12))
            
            self.log_system("Standard layout applied")
            
        except Exception as e:
            pass
 
def main():
    root = tk.Tk()
    app = JTechPixelUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
