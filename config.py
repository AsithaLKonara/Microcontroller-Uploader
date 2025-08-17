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

# Supported devices
SUPPORTED_DEVICES = {
    "ESP8266": "ESP8266 NodeMCU, Wemos D1 Mini",
    "ESP32": "ESP32 DevKit, ESP32-WROOM",
    "ESP32-S3": "ESP32-S3 DevKit, ESP32-S3-WROOM",
    "ESP32-C6": "ESP32-C6 RISC-V based microcontroller",
    "ESP32-H2": "ESP32-H2 Low-power microcontroller",
    "AVR": "Arduino Uno, Nano, Pro Mini",
    "ATtiny85": "ATtiny85 Small AVR microcontroller",
    "ATtiny1614": "ATtiny1614 Modern AVR microcontroller",
    "ATmega2560": "ATmega2560 Large AVR microcontroller",
    "STM32": "STM32F103, STM32F407",
    "STM32F7": "STM32F7 High-performance series",
    "STM32H7": "STM32H7 Ultra-high-performance series",
    "STM32L4": "STM32L4 Low-power series",
    "STM32G0": "STM32G0 Cost-effective series",
    "PIC": "PIC microcontrollers via MPLAB IPE",
    "PIC24": "PIC24 16-bit microcontrollers",
    "dsPIC33": "dsPIC33 Digital Signal Controllers",
    "RP2040": "Raspberry Pi Pico (RP2040)",
    "Arduino-Nano-33-BLE": "Arduino Nano 33 BLE (nRF52840)",
    "Arduino-Nano-RP2040": "Arduino Nano RP2040 Connect",
    "Teensy-4.1": "Teensy 4.1 ARM Cortex-M7",
    "Teensy-3.6": "Teensy 3.6 ARM Cortex-M4",
    "MSP430": "MSP430 Texas Instruments low-power MCU",
    "EFM32": "EFM32 Silicon Labs energy-friendly MCU",
    "LPC": "LPC NXP ARM Cortex-M microcontrollers"
}

# Supported file types
SUPPORTED_FILES = {
    "Firmware files": "*.bin *.hex *.dat *.elf *.uf2",
    "Binary files": "*.bin",
    "Hex files": "*.hex",
    "LED Pattern files": "*.bin *.dat",
    "UF2 files": "*.uf2",
    "All files": "*.*"
}

# Pattern testing configuration
PATTERN_TESTING = {
    "enabled": True,
    "auto_detect": True,
    "custom_protocol": True,
    "auto_reset_after_upload": True,
    "visual_verification": True,
    "supported_devices": ["ESP8266", "ESP32", "ESP32-S3", "ESP32-C6", "ESP32-H2", "RP2040", "Arduino-Nano-33-BLE", "Arduino-Nano-RP2040", "Teensy-4.1", "Teensy-3.6"]
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
        "supported_files": ["*.bin", "*.hex", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "ESP32": {
        "command": "python",
        "args": ["-m", "esptool", "--chip", "esp32", "--port", "{port}", "--baud", "{baud}", "--before", "default-reset", "--after", "hard-reset", "write-flash", "0x1000", "{file}"],
        "description": "ESP32 DevKit, ESP32-WROOM",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16", "32x32"]
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
    },
    "ESP32-S3": {
        "command": "python",
        "args": ["-m", "esptool", "--chip", "esp32s3", "--port", "{port}", "--baud", "{baud}", "--before", "default-reset", "--after", "hard-reset", "write-flash", "0x0", "{file}"],
        "description": "ESP32-S3 DevKit, ESP32-S3-WROOM",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16", "32x32"]
    },
    "ESP32-C6": {
        "command": "python",
        "args": ["-m", "esptool", "--chip", "esp32c6", "--port", "{port}", "--baud", "{baud}", "--before", "default-reset", "--after", "hard-reset", "write-flash", "0x0", "{file}"],
        "description": "ESP32-C6 RISC-V based microcontroller",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "ESP32-H2": {
        "command": "python",
        "args": ["-m", "esptool", "--chip", "esp32h2", "--port", "{port}", "--baud", "{baud}", "--before", "default-reset", "--after", "hard-reset", "write-flash", "0x0", "{file}"],
        "description": "ESP32-H2 Low-power microcontroller",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "RP2040": {
        "command": "python",
        "args": ["-m", "rp2040", "--port", "{port}", "--baud", "{baud}", "write-flash", "{file}"],
        "description": "Raspberry Pi Pico (RP2040)",
        "default_baud": "115200",
        "supported_files": ["*.uf2", "*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "Arduino-Nano-33-BLE": {
        "command": "arduino-cli",
        "args": ["compile", "--fqbn", "arduino:mbed_nano:nano33ble", "--port", "{port}", "upload"],
        "description": "Arduino Nano 33 BLE (nRF52840)",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "Arduino-Nano-RP2040": {
        "command": "arduino-cli",
        "args": ["compile", "--fqbn", "arduino:mbed_rp2040:nano_rp2040_connect", "--port", "{port}", "upload"],
        "description": "Arduino Nano RP2040 Connect",
        "default_baud": "115200",
        "supported_files": ["*.uf2", "*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "Teensy-4.1": {
        "command": "teensy_loader_cli",
        "args": ["--mcu", "imxrt1062", "--port", "{port}", "--write", "{file}"],
        "description": "Teensy 4.1 ARM Cortex-M7",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16", "32x32"]
    },
    "Teensy-3.6": {
        "command": "teensy_loader_cli",
        "args": ["--mcu", "mk66fx1m0", "--port", "{port}", "--write", "{file}"],
        "description": "Teensy 3.6 ARM Cortex-M4",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "STM32F7": {
        "command": "stm32flash",
        "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
        "description": "STM32F7 High-performance series",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex", "*.dat"],
        "led_pattern_support": True,
        "matrix_sizes": ["8x8", "16x16"]
    },
    "STM32H7": {
        "command": "stm32flash",
        "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
        "description": "STM32H7 Ultra-high-performance series",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex"]
    },
    "STM32L4": {
        "command": "stm32flash",
        "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
        "description": "STM32L4 Low-power series",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex"]
    },
    "STM32G0": {
        "command": "stm32flash",
        "args": ["-w", "{file}", "-v", "-g", "0x0", "-b", "{baud}", "{port}"],
        "description": "STM32G0 Cost-effective series",
        "default_baud": "115200",
        "supported_files": ["*.bin", "*.hex"]
    },
    "ATtiny85": {
        "command": "avrdude",
        "args": ["-c", "usbasp", "-p", "attiny85", "-P", "{port}", "-b", "{baud}", "-U", "flash:w:{file}:i"],
        "description": "ATtiny85 Small AVR microcontroller",
        "default_baud": "115200",
        "supported_files": ["*.hex"]
    },
    "ATtiny1614": {
        "command": "avrdude",
        "args": ["-c", "usbasp", "-p", "attiny1614", "-P", "{port}", "-b", "{baud}", "-U", "flash:w:{file}:i"],
        "description": "ATtiny1614 Modern AVR microcontroller",
        "default_baud": "115200",
        "supported_files": ["*.hex"]
    },
    "ATmega2560": {
        "command": "avrdude",
        "args": ["-c", "arduino", "-p", "atmega2560", "-P", "{port}", "-b", "{baud}", "-U", "flash:w:{file}:i"],
        "description": "ATmega2560 Large AVR microcontroller",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin"]
    },
    "PIC24": {
        "command": "mplab_ipe",
        "args": ["-TPICkit3", "-P{port}", "-F{file}", "-M"],
        "description": "PIC24 16-bit microcontrollers",
        "default_baud": "115200",
        "supported_files": ["*.hex"]
    },
    "dsPIC33": {
        "command": "mplab_ipe",
        "args": ["-TPICkit3", "-P{port}", "-F{file}", "-M"],
        "description": "dsPIC33 Digital Signal Controllers",
        "default_baud": "115200",
        "supported_files": ["*.hex"]
    },
    "MSP430": {
        "command": "mspdebug",
        "args": ["tilib", "prog", "{file}"],
        "description": "MSP430 Texas Instruments low-power MCU",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin"]
    },
    "EFM32": {
        "command": "commander",
        "args": ["flash", "--device", "EFM32GG11B820F2048GL192", "--address", "0x00000000", "--file", "{file}"],
        "description": "EFM32 Silicon Labs energy-friendly MCU",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin"]
    },
    "LPC": {
        "command": "lpc21isp",
        "args": ["{file}", "{port}", "{baud}", "12000"],
        "description": "LPC NXP ARM Cortex-M microcontrollers",
        "default_baud": "115200",
        "supported_files": ["*.hex", "*.bin"]
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
    # Primary brand colors
    "primary": "#2563eb",           # Modern blue
    "primary_dark": "#1d4ed8",      # Darker blue for hover
    "primary_light": "#dbeafe",     # Light blue for backgrounds
    
    # Status colors
    "success": "#059669",           # Modern green
    "success_light": "#d1fae5",     # Light green
    "warning": "#d97706",           # Modern orange
    "warning_light": "#fed7aa",     # Light orange
    "error": "#dc2626",             # Modern red
    "error_light": "#fecaca",       # Light red
    "info": "#0891b2",              # Modern cyan
    "info_light": "#cffafe",        # Light cyan
    
    # Neutral colors
    "light": "#f8fafc",             # Very light gray
    "light_gray": "#f1f5f9",        # Light gray
    "gray": "#64748b",              # Medium gray
    "dark": "#1e293b",              # Dark gray
    "darker": "#0f172a",            # Very dark gray
    
    # Accent colors
    "accent": "#7c3aed",            # Purple accent
    "accent_light": "#ede9fe",      # Light purple
    "highlight": "#fbbf24",         # Yellow highlight
    "highlight_light": "#fef3c7"    # Light yellow
}

# Modern UI themes
UI_THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#1e293b",
        "frame_bg": "#f8fafc",
        "button_bg": "#f1f5f9",
        "button_fg": "#1e293b",
        "accent_bg": "#dbeafe",
        "accent_fg": "#1d4ed8"
    },
    "dark": {
        "bg": "#0f172a",
        "fg": "#f1f5f9",
        "frame_bg": "#1e293b",
        "button_bg": "#334155",
        "button_fg": "#f1f5f9",
        "accent_bg": "#1e3a8a",
        "accent_fg": "#dbeafe"
    },
    "blue": {
        "bg": "#f0f9ff",
        "fg": "#0c4a6e",
        "frame_bg": "#e0f2fe",
        "button_bg": "#bae6fd",
        "button_fg": "#0c4a6e",
        "accent_bg": "#0284c7",
        "accent_fg": "#ffffff"
    }
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

# LED Pattern Support Configuration
LED_PATTERN_SUPPORT = {
    "enabled": True,
    "supported_devices": [
        "ESP8266", "ESP32", "ESP32-S3", "ESP32-C6", "ESP32-H2",
        "RP2040", "Arduino-Nano-33-BLE", "Arduino-Nano-RP2040",
        "Teensy-4.1", "Teensy-3.6", "STM32F7"
    ],
    "matrix_sizes": {
        "8x8": {"leds": 64, "bytes": 192, "max_patterns": 10},
        "16x16": {"leds": 256, "bytes": 768, "max_patterns": 5},
        "32x32": {"leds": 1024, "bytes": 3072, "max_patterns": 2}
    },
    "file_formats": [".dat", ".bin"],
    "protocols": ["LEDP", "SPIFFS", "LittleFS"],
    "auto_install_tools": True,
    "pattern_editor": True
}
