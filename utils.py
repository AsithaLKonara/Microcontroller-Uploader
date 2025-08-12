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
        if file_ext not in [".bin", ".hex", ".dat"]:
            return False, f"ESP devices require .bin, .hex, or .dat files, got {file_ext}"
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
        "spiral_8x8.bin": create_spiral_pattern,
        # Add .dat versions
        "alternating_cols_8x8.dat": create_alternating_cols_pattern,
        "checkerboard_8x8.dat": create_checkerboard_pattern,
        "rainbow_8x8.dat": create_rainbow_pattern,
        "pulse_8x8.dat": create_pulse_pattern,
        "spiral_8x8.dat": create_spiral_pattern
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

def create_heart_pattern():
    """Create heart pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), heart shape
    pattern = bytearray()
    
    # Heart pattern matrix (1 = red, 0 = black)
    heart_matrix = [
        [0,0,0,0,0,0,0,0],
        [0,1,1,0,0,1,1,0],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,0,0],
        [0,0,0,1,1,0,0,0]
    ]
    
    for row in range(8):
        for col in range(8):
            if heart_matrix[row][col]:
                pattern.extend([255, 0, 0])  # Red
            else:
                pattern.extend([0, 0, 0])    # Black
    
    return pattern

def create_cross_pattern():
    """Create cross pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), cross shape
    pattern = bytearray()
    
    for row in range(8):
        for col in range(8):
            # Create cross pattern
            if row == 3 or row == 4 or col == 3 or col == 4:
                pattern.extend([0, 255, 0])  # Green
            else:
                pattern.extend([0, 0, 0])    # Black
    
    return pattern

def create_border_pattern():
    """Create border pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), border only
    pattern = bytearray()
    
    for row in range(8):
        for col in range(8):
            # Create border pattern
            if row == 0 or row == 7 or col == 0 or col == 7:
                pattern.extend([0, 0, 255])  # Blue
            else:
                pattern.extend([0, 0, 0])    # Black
    
    return pattern

def create_diagonal_pattern():
    """Create diagonal pattern (8x8 matrix)"""
    # 8x8 matrix, 3 bytes per LED (RGB), diagonal lines
    pattern = bytearray()
    
    for row in range(8):
        for col in range(8):
            # Create diagonal pattern
            if row == col or row + col == 7:
                pattern.extend([255, 255, 0])  # Yellow
            else:
                pattern.extend([0, 0, 0])      # Black
    
    return pattern

def create_sample_dat_files():
    """Create sample .dat files specifically for LED patterns"""
    patterns = {
        "heart_8x8.dat": create_heart_pattern,
        "cross_8x8.dat": create_cross_pattern,
        "border_8x8.dat": create_border_pattern,
        "diagonal_8x8.dat": create_diagonal_pattern,
        "rainbow_rgb_8x8.dat": create_rainbow_pattern
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
            print(f"Created {filename}: {len(pattern_data)} bytes")
        except Exception as e:
            print(f"Error creating {filename}: {e}")
    
    return created_files

def validate_dat_file(file_path: str) -> Tuple[bool, str]:
    """Validate if a .dat file contains valid LED pattern data"""
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        if not file_path.lower().endswith('.dat'):
            return False, "File is not a .dat file"
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return False, "File is empty"
        
        # Check if file size is reasonable for LED patterns
        if file_size > 10240:  # 10KB max for LED patterns
            return False, f"File too large ({file_size} bytes) for LED pattern data"
        
        # Read file and check if it's binary data
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Check if data size is a multiple of 3 (RGB values)
        if len(data) % 3 != 0:
            return False, f"Data size ({len(data)} bytes) is not a multiple of 3 (RGB values)"
        
        # Check if this looks like RGB data
        led_count = len(data) // 3
        if led_count < 1:
            return False, "No LED data found"
        
        # Validate RGB values (should be 0-255)
        for i in range(0, len(data), 3):
            r, g, b = data[i:i+3]
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                return False, f"Invalid RGB values at position {i//3}"
        
        # Determine matrix size
        if led_count == 64:
            matrix_size = "8x8"
        elif led_count == 256:
            matrix_size = "16x16"
        else:
            matrix_size = f"{led_count} LEDs"
        
        return True, f"Valid LED pattern data: {matrix_size} matrix, {len(data)} bytes"
        
    except Exception as e:
        return False, f"Error validating .dat file: {str(e)}"

def get_dat_file_info(file_path: str) -> Dict[str, any]:
    """Get detailed information about a .dat file"""
    try:
        if not os.path.exists(file_path):
            return {"error": "File does not exist"}
        
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        led_count = len(data) // 3 if len(data) % 3 == 0 else 0
        
        info = {
            "file_size": file_size,
            "data_size": len(data),
            "led_count": led_count,
            "is_valid_rgb": len(data) % 3 == 0,
            "matrix_size": None,
            "rgb_values": []
        }
        
        if info["is_valid_rgb"]:
            if led_count == 64:
                info["matrix_size"] = "8x8"
            elif led_count == 256:
                info["matrix_size"] = "16x16"
            else:
                info["matrix_size"] = f"{led_count} LEDs"
            
            # Sample first few RGB values
            sample_count = min(10, led_count)
            for i in range(0, sample_count * 3, 3):
                if i + 2 < len(data):
                    r, g, b = data[i:i+3]
                    info["rgb_values"].append((r, g, b))
        
        return info
        
    except Exception as e:
        return {"error": f"Error reading .dat file: {str(e)}"}

import sys

def check_and_install_dependencies():
    """Check and automatically install required dependencies"""
    print("🔍 Checking required dependencies...")
    
    # Check Python version
    python_version = platform.python_version()
    print(f"🐍 Python version: {python_version}")
    
    # Check if pip is available
    try:
        import pip
        print("📦 pip is available")
    except ImportError:
        print("❌ pip not found - cannot install packages")
        return False
    
    # List of required packages
    required_packages = {
        "esptool": "esptool",
        "pyserial": "serial",
        "tkinter": "tkinter"
    }
    
    missing_packages = []
    
    # Check each package
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} is available")
        except ImportError:
            print(f"❌ {package_name} not found")
            missing_packages.append(package_name)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        
        for package in missing_packages:
            try:
                print(f"📦 Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package, "--user"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout installing {package}")
                return False
            except Exception as e:
                print(f"❌ Error installing {package}: {e}")
                return False
    
    print("🎉 All dependencies are available!")
    return True

def install_esptool():
    """Install esptool if not available"""
    try:
        print("📥 Installing esptool...")
        
        # Try to install esptool
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "esptool", "--user"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ esptool installed successfully")
            return True
        else:
            print(f"❌ Failed to install esptool: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout installing esptool")
        return False
    except Exception as e:
        print(f"❌ Error installing esptool: {e}")
        return False

def check_python_version():
    """Check if Python version meets requirements"""
    version = platform.python_version_tuple()
    major, minor = int(version[0]), int(version[1])
    
    if major < 3 or (major == 3 and minor < 7):
        return False, f"Python {major}.{minor} detected. Python 3.7+ is required."
    
    return True, f"Python {major}.{minor} - Version OK"

def get_system_dependencies():
    """Get information about system dependencies"""
    dependencies = {
        "python": {
            "required": "3.7+",
            "current": platform.python_version(),
            "status": "unknown"
        },
        "pip": {
            "required": "Available",
            "current": "Unknown",
            "status": "unknown"
        },
        "esptool": {
            "required": "Available",
            "current": "Unknown",
            "status": "unknown"
        },
        "pyserial": {
            "required": "Available",
            "current": "Unknown",
            "status": "unknown"
        }
    }
    
    # Check Python version
    python_ok, python_msg = check_python_version()
    dependencies["python"]["status"] = "✅ OK" if python_ok else "❌ Too old"
    
    # Check pip
    try:
        import pip
        dependencies["pip"]["current"] = pip.__version__
        dependencies["pip"]["status"] = "✅ Available"
    except ImportError:
        dependencies["pip"]["current"] = "Not found"
        dependencies["pip"]["status"] = "❌ Missing"
    
    # Check esptool
    esptool_path = find_esptool()
    if esptool_path:
        dependencies["esptool"]["current"] = "Found"
        dependencies["esptool"]["status"] = "✅ Available"
    else:
        dependencies["esptool"]["current"] = "Not found"
        dependencies["esptool"]["status"] = "❌ Missing"
    
    # Check pyserial
    try:
        import serial
        dependencies["pyserial"]["current"] = serial.__version__
        dependencies["pyserial"]["status"] = "✅ Available"
    except ImportError:
        dependencies["pyserial"]["current"] = "Not found"
        dependencies["pyserial"]["status"] = "❌ Missing"
    
    return dependencies

def auto_fix_dependencies():
    """Automatically fix missing dependencies"""
    print("🔧 Auto-fixing dependencies...")
    
    dependencies = get_system_dependencies()
    fixed_count = 0
    
    # Fix pip if missing
    if dependencies["pip"]["status"] == "❌ Missing":
        print("📥 Installing pip...")
        # This would require more complex logic to install pip
        print("⚠️ pip installation requires manual intervention")
    
    # Fix esptool if missing
    if dependencies["esptool"]["status"] == "❌ Missing":
        print("📥 Installing esptool...")
        if install_esptool():
            fixed_count += 1
    
    # Fix pyserial if missing
    if dependencies["pyserial"]["status"] == "❌ Missing":
        print("📥 Installing pyserial...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "pyserial", "--user"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ pyserial installed successfully")
                fixed_count += 1
            else:
                print(f"❌ Failed to install pyserial: {result.stderr}")
        except Exception as e:
            print(f"❌ Error installing pyserial: {e}")
    
    print(f"🎉 Fixed {fixed_count} dependencies automatically")
    return fixed_count
