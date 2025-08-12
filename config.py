# J Tech Pixel Uploader Configuration
# This file contains all the configuration settings for the application

import os
import json

# Application settings
APP_NAME = "J Tech Pixel Uploader"
APP_VERSION = "1.0.0"
APP_AUTHOR = "J Tech Pixel"
APP_DESCRIPTION = "Professional firmware uploader for microcontrollers"

# Default settings
DEFAULT_BAUD_RATE = "115200"
DEFAULT_DEVICE = "ESP8266"
DEFAULT_WINDOW_SIZE = "800x600"

# Supported file types
SUPPORTED_FILES = {
    "Firmware files": "*.bin *.hex *.dat *.elf",
    "Binary files": "*.bin",
    "Hex files": "*.hex",
    "LED Pattern files": "*.bin *.dat",
    "All files": "*.*"
}

# Pattern testing configuration
PATTERN_TESTING = {
    "enabled": True,
    "auto_detect": True,
    "custom_protocol": True,
    "auto_reset_after_upload": True,
    "visual_verification": True,
    "supported_devices": ["ESP8266", "ESP32"]
}

# LED Matrix configurations
LED_MATRIX_CONFIGS = {
    "8x8": {
        "width": 8,
        "height": 8,
        "total_leds": 64,
        "bytes_per_led": 3,  # RGB
        "total_bytes": 192,
        "supported_patterns": ["alternating", "checkerboard", "rainbow", "pulse", "spiral"]
    },
    "16x16": {
        "width": 16,
        "height": 16,
        "total_leds": 256,
        "bytes_per_led": 3,  # RGB
        "total_bytes": 768,
        "supported_patterns": ["alternating", "checkerboard", "rainbow", "pulse", "spiral"]
    }
}

# Device configurations
DEVICE_CONFIGS = {
    "ESP8266": {
        "command": "python",
        "args": ["-m", "esptool", "--port", "{port}", "--baud", "{baud}", "--before", "default-reset", "--after", "hard-reset", "write-flash", "0x00000", "{file}"],
        "description": "ESP8266 NodeMCU, Wemos D1 Mini",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex"]
    },
    "ESP32": {
        "command": "python",
        "args": ["-m", "esptool", "--chip", "esp32", "--port", "{port}", "--baud", "{baud}", "--before", "default-reset", "--after", "hard-reset", "write-flash", "0x1000", "{file}"],
        "description": "ESP32 DevKit, ESP32-WROOM",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex"]
    },
    "AVR": {
        "command": "avrdude",
        "args": ["-c", "arduino", "-p", "atmega328p", "-P", "{port}", "-b", "{baud}", "-U", "flash:w:{file}:i"],
        "description": "Arduino Uno, Nano, Pro Mini",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin"]
    },
    "STM32": {
        "command": "stm32flash",
        "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
        "description": "STM32F103, STM32F407",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex"]
    },
    "PIC": {
        "command": "mplab_ipe",
        "args": ["-TPICkit3", "-P{port}", "-F{file}", "-M"],
        "description": "PIC microcontrollers via MPLAB IPE",
        "default_baud": "115200",
        "supported_files": ["*.hex"]
    }
}

# Baud rate options
BAUD_RATES = [
    "9600", "19200", "38400", "57600", "115200", 
    "230400", "460800", "921600", "1500000", "2000000"
]

# Advanced esptool options for better reset control
ESPTOOL_RESET_OPTIONS = {
    "before_reset": [
        "default-reset",    # Use DTR/RTS lines to reset into bootloader
        "no-reset",         # Skip reset, useful if hardware isn't wired for reset
        "usb-reset"         # USB reset (ESP32 only)
    ],
    "after_reset": [
        "hard-reset",       # Hard reset after upload
        "soft-reset",       # Soft reset after upload  
        "no-reset"          # No reset after upload
    ]
}

# Recommended reset combinations for different scenarios
RECOMMENDED_RESET_COMBINATIONS = {
    "auto_flash": ("default-reset", "hard-reset"),      # Standard auto-flash
    "manual_reset": ("no-reset", "hard-reset"),         # Manual reset before upload
    "no_reset": ("no-reset", "no-reset"),               # No reset at all
    "force_flash": ("usb-reset", "hard-reset")          # Force flash mode (ESP32)
}

# UI Colors and styling
UI_COLORS = {
    "primary": "#007acc",
    "success": "#28a745",
    "warning": "#ffc107",
    "error": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Logging configuration
LOG_CONFIG = {
    "max_log_lines": 1000,
    "timestamp_format": "%H:%M:%S",
    "date_format": "%Y-%m-%d %H:%M:%S"
}

# File paths
def get_config_dir():
    """Get the configuration directory for the application"""
    if os.name == 'nt':  # Windows
        config_dir = os.path.join(os.environ.get('APPDATA', ''), 'JTechPixelUploader')
    else:  # Linux/Mac
        config_dir = os.path.join(os.path.expanduser('~'), '.config', 'JTechPixelUploader')
    
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_config_file():
    """Get the configuration file path"""
    return os.path.join(get_config_dir(), 'config.json')

def load_config():
    """Load configuration from file"""
    config_file = get_config_file()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(config):
    """Save configuration to file"""
    config_file = get_config_file()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except:
        return False

# Default configuration
DEFAULT_CONFIG = {
    "last_firmware_path": "",
    "last_com_port": "",
    "last_device": DEFAULT_DEVICE,
    "last_baud_rate": DEFAULT_BAUD_RATE,
    "window_size": DEFAULT_WINDOW_SIZE,
    "auto_detect_ports": True,
    "show_timestamps": True,
    "theme": "clam"
}
