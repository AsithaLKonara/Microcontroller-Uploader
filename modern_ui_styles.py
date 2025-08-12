#!/usr/bin/env python3
"""
Modern UI Styling Module for J Tech Pixel Uploader
Provides enhanced visual design, modern styling, and professional appearance
"""

import tkinter as tk
from tkinter import ttk
import config

class ModernUIStyles:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.setup_modern_styles()
        self.apply_modern_theme()
    
    def setup_modern_styles(self):
        """Setup modern, professional styles for all UI elements"""
        
        # Configure the root style
        self.style.theme_use('clam')
        
        # Modern button styles
        self.style.configure("Modern.TButton",
                           background=config.UI_COLORS["primary"],
                           foreground="white",
                           borderwidth=0,
                           focuscolor="none",
                           font=("Segoe UI", 9, "normal"),
                           padding=(12, 8))
        
        self.style.map("Modern.TButton",
                      background=[("active", config.UI_COLORS["primary_dark"]),
                                ("pressed", config.UI_COLORS["primary_dark"])])
        
        # Success button style
        self.style.configure("Success.TButton",
                           background=config.UI_COLORS["success"],
                           foreground="white",
                           borderwidth=0,
                           focuscolor="none",
                           font=("Segoe UI", 9, "bold"),
                           padding=(12, 8))
        
        self.style.map("Success.TButton",
                      background=[("active", config.UI_COLORS["success_light"]),
                                ("pressed", config.UI_COLORS["success_light"])])
        
        # Warning button style
        self.style.configure("Warning.TButton",
                           background=config.UI_COLORS["warning"],
                           foreground="white",
                           borderwidth=0,
                           focuscolor="none",
                           font=("Segoe UI", 9, "normal"),
                           padding=(12, 8))
        
        # Error button style
        self.style.configure("Error.TButton",
                           background=config.UI_COLORS["error"],
                           foreground="white",
                           borderwidth=0,
                           focuscolor="none",
                           font=("Segoe UI", 9, "normal"),
                           padding=(12, 8))
        
        # Info button style
        self.style.configure("Info.TButton",
                           background=config.UI_COLORS["info"],
                           foreground="white",
                           borderwidth=0,
                           focuscolor="none",
                           font=("Segoe UI", 9, "normal"),
                           padding=(12, 8))
        
        # Accent button style
        self.style.configure("Accent.TButton",
                           background=config.UI_COLORS["accent"],
                           foreground="white",
                           borderwidth=0,
                           focuscolor="none",
                           font=("Segoe UI", 9, "bold"),
                           padding=(12, 8))
        
        # Modern frame styles
        self.style.configure("Modern.TFrame",
                           background=config.UI_COLORS["light"],
                           relief="flat",
                           borderwidth=0)
        
        # Modern label frame styles
        self.style.configure("Modern.TLabelframe",
                           background=config.UI_COLORS["light"],
                           relief="flat",
                           borderwidth=1,
                           bordercolor=config.UI_COLORS["light_gray"])
        
        self.style.configure("Modern.TLabelframe.Label",
                           background=config.UI_COLORS["light"],
                           foreground=config.UI_COLORS["dark"],
                           font=("Segoe UI", 10, "bold"))
        
        # Modern label styles
        self.style.configure("Title.TLabel",
                           background=config.UI_COLORS["light"],
                           foreground=config.UI_COLORS["primary"],
                           font=("Segoe UI", 16, "bold"))
        
        self.style.configure("Subtitle.TLabel",
                           background=config.UI_COLORS["light"],
                           foreground=config.UI_COLORS["gray"],
                           font=("Segoe UI", 12, "normal"))
        
        self.style.configure("Status.TLabel",
                           background=config.UI_COLORS["light"],
                           foreground=config.UI_COLORS["success"],
                           font=("Segoe UI", 10, "bold"))
        
        # Modern entry styles
        self.style.configure("Modern.TEntry",
                           fieldbackground="white",
                           borderwidth=1,
                           bordercolor=config.UI_COLORS["light_gray"],
                           focuscolor=config.UI_COLORS["primary"],
                           font=("Segoe UI", 9, "normal"),
                           padding=(8, 6))
        
        # Modern combobox styles
        self.style.configure("Modern.TCombobox",
                           fieldbackground="white",
                           borderwidth=1,
                           bordercolor=config.UI_COLORS["light_gray"],
                           focuscolor=config.UI_COLORS["primary"],
                           font=("Segoe UI", 9, "normal"),
                           padding=(8, 6))
        
        # Modern progress bar styles
        self.style.configure("Modern.Horizontal.TProgressbar",
                           background=config.UI_COLORS["primary"],
                           troughcolor=config.UI_COLORS["light_gray"],
                           borderwidth=0,
                           lightcolor=config.UI_COLORS["primary"],
                           darkcolor=config.UI_COLORS["primary"])
        
        # Modern scrollbar styles
        self.style.configure("Modern.Vertical.TScrollbar",
                           background=config.UI_COLORS["light_gray"],
                           bordercolor=config.UI_COLORS["light_gray"],
                           arrowcolor=config.UI_COLORS["gray"],
                           troughcolor=config.UI_COLORS["light"],
                           width=12)
    
    def apply_modern_theme(self):
        """Apply the modern theme to the root window"""
        self.root.configure(bg=config.UI_COLORS["light"])
        
        # Configure modern colors for text widgets
        self.root.option_add('*Text.background', 'white')
        self.root.option_add('*Text.foreground', config.UI_COLORS["dark"])
        self.root.option_add('*Text.insertBackground', config.UI_COLORS["primary"])
        self.root.option_add('*Text.selectBackground', config.UI_COLORS["primary_light"])
        self.root.option_add('*Text.selectForeground', config.UI_COLORS["dark"])
        self.root.option_add('*Text.font', ('Segoe UI', 9))
        
        # Configure modern colors for canvas
        self.root.option_add('*Canvas.background', 'white')
        self.root.option_add('*Canvas.borderwidth', '1')
        self.root.option_add('*Canvas.relief', 'solid')
    
    def create_modern_button(self, parent, text, command, style="Modern.TButton", **kwargs):
        """Create a modern button with consistent styling"""
        return ttk.Button(parent, text=text, command=command, style=style, **kwargs)
    
    def create_modern_frame(self, parent, **kwargs):
        """Create a modern frame with consistent styling"""
        return ttk.Frame(parent, style="Modern.TFrame", **kwargs)
    
    def create_modern_label_frame(self, parent, text, **kwargs):
        """Create a modern label frame with consistent styling"""
        return ttk.LabelFrame(parent, text=text, style="Modern.TLabelframe", **kwargs)
    
    def create_modern_entry(self, parent, **kwargs):
        """Create a modern entry with consistent styling"""
        return ttk.Entry(parent, style="Modern.TEntry", **kwargs)
    
    def create_modern_combobox(self, parent, **kwargs):
        """Create a modern combobox with consistent styling"""
        return ttk.Combobox(parent, style="Modern.TCombobox", **kwargs)
    
    def create_modern_progress_bar(self, parent, **kwargs):
        """Create a modern progress bar with consistent styling"""
        return ttk.Progressbar(parent, style="Modern.Horizontal.TProgressbar", **kwargs)
    
    def create_modern_scrollbar(self, parent, **kwargs):
        """Create a modern scrollbar with consistent styling"""
        return ttk.Scrollbar(parent, style="Modern.Vertical.TScrollbar", **kwargs)
    
    def get_modern_colors(self):
        """Get the modern color palette"""
        return config.UI_COLORS
    
    def apply_hover_effects(self, widget, hover_color, normal_color):
        """Apply hover effects to a widget"""
        def on_enter(e):
            widget.configure(background=hover_color)
        
        def on_leave(e):
            widget.configure(background=normal_color)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
