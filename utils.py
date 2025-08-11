# J Tech Pixel Uploader Utilities
# Helper functions and utilities for the application

import os
import subprocess
import platform
import shutil
from typing import List, Dict, Optional, Tuple

def check_command_available(command: str) -> bool:
    """Check if a command is available in the system PATH"""
    return shutil.which(command) is not None

def get_system_info() -> Dict[str, str]:
    """Get system information"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "machine": platform.machine()
    }

def find_esptool():
    """Find esptool installation"""
    # Try different possible locations
    possible_paths = [
        "esptool",  # If in PATH
        "esptool.py",  # Direct script
        "python -m esptool",  # As Python module
    ]
    
    for path in possible_paths:
        try:
            if path.startswith("python -m"):
                # Test Python module
                result = subprocess.run(["python", "-m", "esptool", "--help"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return "python -m esptool"
            else:
                # Test direct command
                result = subprocess.run([path, "--help"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return path
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            continue
    
    return None

def find_avrdude() -> Optional[str]:
    """Find avrdude in the system"""
    if check_command_available("avrdude"):
        return "avrdude"
    return None

def find_stm32flash() -> Optional[str]:
    """Find stm32flash in the system"""
    if check_command_available("stm32flash"):
        return "stm32flash"
    return None

def find_mplab_ipe() -> Optional[str]:
    """Find MPLAB IPE in the system"""
    if platform.system() == "Windows":
        # Common MPLAB IPE installation paths on Windows
        possible_paths = [
            r"C:\Program Files\Microchip\MPLABX\v6.15\mplab_platform\bin\mplab_ipe.exe",
            r"C:\Program Files (x86)\Microchip\MPLABX\v6.15\mplab_platform\bin\mplab_ipe.exe",
            r"C:\Program Files\Microchip\MPLABX\v6.10\mplab_platform\bin\mplab_ipe.exe",
            r"C:\Program Files (x86)\Microchip\MPLABX\v6.10\mplab_platform\bin\mplab_ipe.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    # Check if it's available as a command
    if check_command_available("mplab_ipe"):
        return "mplab_ipe"
    
    return None

def get_available_tools() -> Dict[str, bool]:
    """Get a dictionary of available flashing tools"""
    return {
        "esptool": find_esptool() is not None,
        "avrdude": find_avrdude() is not None,
        "stm32flash": find_stm32flash() is not None,
        "mplab_ipe": find_mplab_ipe() is not None
    }

def validate_firmware_file(file_path: str, device_type: str) -> Tuple[bool, str]:
    """Validate if a firmware file is suitable for the selected device"""
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not os.path.isfile(file_path):
        return False, "Path is not a file"
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "File is empty"
    
    # Check file extension based on device type
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if device_type in ["ESP8266", "ESP32"]:
        if file_ext not in [".bin", ".hex"]:
            return False, f"ESP devices require .bin or .hex files, got {file_ext}"
    elif device_type == "AVR":
        if file_ext != ".hex":
            return False, f"AVR devices require .hex files, got {file_ext}"
    elif device_type == "STM32":
        if file_ext not in [".bin", ".hex"]:
            return False, f"STM32 devices require .bin or .hex files, got {file_ext}"
    elif device_type == "PIC":
        if file_ext != ".hex":
            return False, f"PIC devices require .hex files, got {file_ext}"
    
    return True, "File is valid"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def get_file_info(file_path: str) -> Dict[str, str]:
    """Get information about a firmware file"""
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    return {
        "name": os.path.basename(file_path),
        "size": format_file_size(stat.st_size),
        "size_bytes": str(stat.st_size),
        "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
        "extension": os.path.splitext(file_path)[1].lower()
    }

def run_command_with_output(command: List[str], timeout: int = 300) -> Tuple[int, str, str]:
    """Run a command and capture its output with timeout"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def is_port_available(port: str) -> bool:
    """Check if a COM port is available"""
    try:
        import serial
        ser = serial.Serial(port, timeout=1)
        ser.close()
        return True
    except:
        return False

def get_port_info(port: str) -> Dict[str, str]:
    """Get information about a COM port"""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if p.device == port:
                return {
                    "device": p.device,
                    "description": p.description or "Unknown",
                    "manufacturer": p.manufacturer or "Unknown",
                    "product": p.product or "Unknown",
                    "hwid": p.hwid or "Unknown"
                }
    except:
        pass
    
    return {"device": port, "description": "Unknown", "manufacturer": "Unknown", "product": "Unknown", "hwid": "Unknown"}

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe use"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    
    return filename

def create_backup_filename(original_path: str) -> str:
    """Create a backup filename for a firmware file"""
    base_name = os.path.splitext(original_path)[0]
    extension = os.path.splitext(original_path)[1]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_backup_{timestamp}{extension}"

# Import time module for timestamp functions
import time

def create_sample_led_patterns():
    """Create sample LED pattern files for testing"""
    patterns = {
        "alternating_cols_8x8.bin": create_alternating_cols_pattern,
        "checkerboard_8x8.bin": create_checkerboard_pattern,
        "rainbow_8x8.bin": create_rainbow_pattern,
        "pulse_8x8.bin": create_pulse_pattern,
        "spiral_8x8.bin": create_spiral_pattern
    }
    
    sample_dir = "SampleFirmware"
    os.makedirs(sample_dir, exist_ok=True)
    
    created_files = []
    for filename, pattern_func in patterns.items():
        filepath = os.path.join(sample_dir, filename)
        try:
            pattern_data = pattern_func()
            with open(filepath, 'wb') as f:
                f.write(pattern_data)
            created_files.append(filename)
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    return created_files

def create_alternating_cols_pattern():
    """Create alternating columns pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), alternating columns
    pattern = bytearray()
    for row in range(8):
        for col in range(8):
            if col % 2 == 0:
                # Red column
                pattern.extend([255, 0, 0])  # Red
            else:
                # Blue column
                pattern.extend([0, 0, 255])  # Blue
    return pattern

def create_checkerboard_pattern():
    """Create checkerboard pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), checkerboard
    pattern = bytearray()
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                # White squares
                pattern.extend([255, 255, 255])  # White
            else:
                # Black squares
                pattern.extend([0, 0, 0])  # Black
    return pattern

def create_rainbow_pattern():
    """Create rainbow pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), rainbow effect
    pattern = bytearray()
    colors = [
        [255, 0, 0],    # Red
        [255, 127, 0],  # Orange
        [255, 255, 0],  # Yellow
        [0, 255, 0],    # Green
        [0, 0, 255],    # Blue
        [75, 0, 130],   # Indigo
        [148, 0, 211]   # Violet
    ]
    
    for row in range(8):
        for col in range(8):
            color_idx = (row + col) % len(colors)
            pattern.extend(colors[color_idx])
    return pattern

def create_pulse_pattern():
    """Create pulse pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), pulsing from center
    pattern = bytearray()
    center = 3.5  # Center of 8x8 matrix
    
    for row in range(8):
        for col in range(8):
            # Calculate distance from center
            distance = ((row - center) ** 2 + (col - center) ** 2) ** 0.5
            # Create pulsing effect
            intensity = int(255 * (1 - distance / 5.5))
            intensity = max(0, min(255, intensity))
            pattern.extend([intensity, intensity, intensity])  # Grayscale
    return pattern

def create_spiral_pattern():
    """Create spiral pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), spiral from center
    pattern = bytearray()
    
    # Create spiral order
    spiral_order = []
    for i in range(64):
        spiral_order.append(i)
    
    # Simple spiral pattern - just use position for color
    for i in range(64):
        # Use position to create color variation
        r = (i * 7) % 256
        g = (i * 11) % 256
        b = (i * 13) % 256
        pattern.extend([r, g, b])
    
    return pattern
