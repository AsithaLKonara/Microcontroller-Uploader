#!/usr/bin/env python3
"""
Enhanced UI Layout Module for J Tech Pixel Uploader
Provides improved layout organization, better spacing, and modern design patterns
"""

import tkinter as tk
from tkinter import ttk
import config

class EnhancedUILayout:
    def __init__(self, root, modern_styles):
        self.root = root
        self.modern_styles = modern_styles
        self.colors = modern_styles.get_modern_colors()
        
    def create_header_section(self, parent):
        """Create a modern header section with title and branding"""
        header_frame = ttk.Frame(parent)
        header_frame.configure(padding="20 15")
        
        # Main title with modern styling
        title_label = ttk.Label(header_frame, 
                               text="🚀 J Tech Pixel Uploader", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                  text="Professional Firmware Uploader for Microcontrollers", 
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Version and status info
        version_frame = ttk.Frame(header_frame)
        version_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.E, tk.N, tk.S), padx=(20, 0))
        
        version_label = ttk.Label(version_frame, 
                                 text=f"v{config.APP_VERSION}", 
                                 style="Subtitle.TLabel")
        version_label.grid(row=0, column=0, sticky=tk.E)
        
        status_indicator = ttk.Label(version_frame, 
                                    text="●", 
                                    foreground=self.colors["success"], 
                                    font=("Segoe UI", 16, "bold"))
        status_indicator.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        return header_frame
    
    def create_feature_card(self, parent, title, icon, content_widgets, actions=None):
        """Create a modern feature card with consistent styling"""
        card_frame = ttk.LabelFrame(parent, text=f"{icon} {title}")
        card_frame.configure(padding="15")
        
        # Content area
        content_frame = ttk.Frame(card_frame)
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Add content widgets
        for i, widget in enumerate(content_widgets):
            widget.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Actions area (if provided)
        if actions:
            actions_frame = ttk.Frame(card_frame)
            actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            for i, (text, command, style) in enumerate(actions):
                btn = ttk.Button(actions_frame, text=text, command=command)
                btn.grid(row=0, column=i, padx=(0, 10) if i < len(actions) - 1 else (0, 0))
        
        return card_frame
    
    def create_control_panel(self, parent, app_instance):
        """Create a modern control panel with organized sections"""
        control_frame = ttk.Frame(parent)
        control_frame.configure(padding="10")
        
        # Device selection section
        device_section = self.create_feature_card(
            control_frame,
            "Device Configuration",
            "🔌",
            [
                ttk.Label(control_frame, text="Select your microcontroller type:"),
                ttk.Combobox(control_frame, textvariable=app_instance.selected_device, 
                            values=list(config.SUPPORTED_DEVICES.keys()), state="readonly"),
                ttk.Label(control_frame, text="Choose COM port:"),
                ttk.Combobox(control_frame, textvariable=app_instance.selected_port, state="readonly")
            ],
            [
                ("🔄 Refresh", app_instance.detect_ports, "Info.TButton"),
                ("🔍 Auto-detect", app_instance.auto_detect_port, "Accent.TButton")
            ]
        )
        device_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Firmware selection section
        firmware_section = self.create_feature_card(
            control_frame,
            "Firmware Selection",
            "📁",
            [
                ttk.Label(control_frame, text="Select firmware file to upload:"),
                ttk.Label(control_frame, text="No firmware selected", foreground="gray")
            ],
            [
                ("📂 Browse", app_instance.browse_firmware, "Modern.TButton"),
                ("🧪 Validate", lambda: app_instance.test_connection(), "Info.TButton")
            ]
        )
        firmware_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Upload control section
        upload_section = self.create_feature_card(
            control_frame,
            "Upload Control",
            "🚀",
            [
                ttk.Label(control_frame, text="Ready to upload firmware"),
                ttk.Progressbar(control_frame, mode="determinate", length=200)
            ],
            [
                ("🚀 Upload Firmware", app_instance.upload_firmware, "Success.TButton"),
                ("🧪 Test Connection", app_instance.test_connection, "Info.TButton"),
                ("📊 History", app_instance.show_upload_logs, "Modern.TButton")
            ]
        )
        upload_section.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        return control_frame
    
    def create_advanced_features_panel(self, parent, app_instance):
        """Create a panel for advanced features and tools"""
        features_frame = ttk.Frame(parent)
        features_frame.configure(padding="10")
        
        # Preview uploaded pattern section
        preview_section = self.create_feature_card(
            features_frame,
            "Preview Uploaded Pattern",
            "🎨",
            [
                ttk.Label(features_frame, text="Preview patterns from uploaded firmware or device memory"),
                ttk.Label(features_frame, text="Supports .dat, .bin, and other firmware formats"),
                ttk.Label(features_frame, text="Real-time pattern visualization and animation")
            ],
            [
                ("🎨 Open Preview", app_instance.show_pattern_preview, "Success.TButton"),
                ("🔍 Load Pattern", lambda: app_instance.load_pattern_for_preview("firmware", "static", "8", "8", "WS2812B"), "Info.TButton")
            ]
        )
        preview_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Pattern preview section
        pattern_section = self.create_feature_card(
            features_frame,
            "Real-time Pattern Preview",
            "🎨",
            [
                tk.Canvas(features_frame, width=200, height=200, bg="black", relief="solid", bd=1)
            ],
            [
                ("🔍 Test", app_instance.test_pattern, "Info.TButton"),
                ("🎬 Animate", app_instance.animate_pattern, "Accent.TButton"),
                ("💾 Save", app_instance.save_pattern, "Modern.TButton")
            ]
        )
        pattern_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Matrix configuration section
        matrix_section = self.create_feature_card(
            features_frame,
            "LED Matrix Configuration",
            "⚙️",
            [
                ttk.Frame(features_frame),
                ttk.Label(features_frame, text="Matrix dimensions:"),
                ttk.Frame(features_frame),
                ttk.Label(features_frame, text="LED type:"),
                ttk.Combobox(features_frame, textvariable=getattr(app_instance, 'led_type', tk.StringVar(value="WS2812B")), 
                            values=["WS2812B", "WS2811", "SK6812"], state="readonly")
            ],
            [
                ("🔧 Auto-detect", app_instance.auto_detect_matrix, "Info.TButton"),
                ("📋 Generate Code", app_instance.generate_matrix_code, "Accent.TButton"),
                ("💡 Test", app_instance.test_matrix_config, "Modern.TButton")
            ]
        )
        matrix_section.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Device management section
        device_mgmt_section = self.create_feature_card(
            features_frame,
            "Device Management",
            "📱",
            [
                ttk.Label(features_frame, text="Device Status: Ready"),
                ttk.Label(features_frame, text="Click buttons below to manage device")
            ],
            [
                ("💚 Health Check", app_instance.check_device_health, "Success.TButton"),
                ("📊 Memory Status", app_instance.show_memory_status, "Info.TButton"),
                ("🔄 Refresh", app_instance.refresh_device_status, "Modern.TButton")
            ]
        )
        device_mgmt_section.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        return features_frame
    
    def create_log_panel(self, parent, app_instance):
        """Create a modern log display panel"""
        log_frame = ttk.LabelFrame(parent, text="📋 Upload Logs & Output")
        log_frame.configure(padding="15")
        
        # Log controls
        controls_frame = ttk.Frame(log_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        clear_btn = ttk.Button(controls_frame, text="🗑️ Clear", command=app_instance.clear_log)
        clear_btn.grid(row=0, column=0, padx=(0, 10))
        
        save_btn = ttk.Button(controls_frame, text="💾 Save", command=app_instance.save_log)
        save_btn.grid(row=0, column=1, padx=(0, 10))
        
        open_btn = ttk.Button(controls_frame, text="📁 Open Folder", command=app_instance.open_logs_folder)
        open_btn.grid(row=0, column=2)
        
        # Log text area
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_text = tk.Text(log_text_frame, wrap=tk.WORD, width=int(60), height=int(30))
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        log_text_frame.columnconfigure(0, weight=1)
        log_text_frame.rowconfigure(0, weight=1)
        
        return log_frame, log_text
    
    def create_status_bar(self, parent, app_instance):
        """Create a modern status bar at the bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.configure(padding="10 5")
        
        # Status indicators
        status_label = ttk.Label(status_frame, text="Ready", style="Status.TLabel")
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Activity indicator
        activity_label = ttk.Label(status_frame, text="●", foreground="green", font=("Segoe UI", 12, "bold"))
        activity_label.grid(row=0, column=1, padx=(10, 0))
        
        # Connection status
        connection_label = ttk.Label(status_frame, text="Disconnected", foreground="gray", font=("Segoe UI", 9))
        connection_label.grid(row=0, column=2, padx=(20, 0))
        
        # Theme selector
        theme_label = ttk.Label(status_frame, text="Theme:", font=("Segoe UI", 9))
        theme_label.grid(row=0, column=3, padx=(20, 5), sticky=tk.E)
        
        theme_combo = ttk.Combobox(status_frame, textvariable=getattr(app_instance, 'current_theme', tk.StringVar(value="clam")), 
                                  values=["clam", "alt", "default", "classic"], state="readonly", width=8)
        theme_combo.grid(row=0, column=4, sticky=tk.E)
        theme_combo.bind("<<ComboboxSelected>>", getattr(app_instance, 'change_theme', lambda e: None))
        
        return status_frame
    
    def apply_modern_spacing(self, widget, padding="10", margin="5"):
        """Apply consistent modern spacing to a widget"""
        if hasattr(widget, 'configure'):
            widget.configure(padding=padding)
        return widget
