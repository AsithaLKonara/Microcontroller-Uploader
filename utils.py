# J Tech Pixel Uploader Utilities
# Helper functions and utilities for the application

import os
import subprocess
import platform
import shutil
import hashlib
import tempfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import urllib.request
import zipfile

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

def find_rp2040_tool() -> Optional[str]:
    """Find RP2040 flashing tool"""
    try:
        result = subprocess.run(["python", "-m", "rp2040", "--help"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "python -m rp2040"
    except:
        pass
    
    if check_command_available("rp2040"):
        return "rp2040"
    
    return None

def find_arduino_cli() -> Optional[str]:
    """Find Arduino CLI tool"""
    if check_command_available("arduino-cli"):
        return "arduino-cli"
    return None

def find_teensy_loader() -> Optional[str]:
    """Find Teensy Loader CLI tool"""
    if check_command_available("teensy_loader_cli"):
        return "teensy_loader_cli"
    return None

def find_mspdebug() -> Optional[str]:
    """Find MSPDebug tool for MSP430"""
    if check_command_available("mspdebug"):
        return "mspdebug"
    return None

def find_commander() -> Optional[str]:
    """Find Silicon Labs Commander tool for EFM32"""
    if check_command_available("commander"):
        return "commander"
    return None

def find_lpc21isp() -> Optional[str]:
    """Find LPC21ISP tool for LPC microcontrollers"""
    if check_command_available("lpc21isp"):
        return "lpc21isp"
    return None

def find_hex_converter() -> Optional[str]:
    """Find a HEX to BIN converter tool"""
    # Try srec_cat first (most reliable)
    if check_command_available("srec_cat"):
        return "srec_cat"
    
    # Try objcopy as fallback
    if check_command_available("objcopy"):
        return "objcopy"
    
    # Try hex2bin
    if check_command_available("hex2bin"):
        return "hex2bin"
    
    return None

def download_and_install_fs_tools() -> Tuple[bool, str]:
    """
    Automatically download and install filesystem tools (mkspiffs/mklittlefs)
    Returns: (success, message)
    """
    try:
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Determine architecture
        if "x86_64" in machine or "amd64" in machine:
            arch = "x64"
        elif "x86" in machine or "i386" in machine:
            arch = "x86"
        elif "arm" in machine:
            arch = "arm"
        else:
            arch = "x64"  # Default fallback
        
        # Create tools directory
        tools_dir = Path.home() / ".jtech_uploader" / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        # Download URLs for different platforms - Fixed with working URLs
        tool_urls = {
            "mkspiffs": {
                "windows": "https://github.com/igrr/mkspiffs/releases/download/0.2.3/mkspiffs-0.2.3-arduino-esp32-win32.zip",
                "linux": "https://github.com/igrr/mkspiffs/releases/download/0.2.3/mkspiffs-0.2.3-arduino-esp32-linux64.tar.gz",
                "darwin": "https://github.com/igrr/mkspiffs/releases/download/0.2.3/mkspiffs-0.2.3-arduino-esp32-osx.tar.gz"
            },
            "mklittlefs": {
                "windows": "https://github.com/littlefs-project/littlefs/releases/download/v2.5.0/mklittlefs-2.5.0-windows-amd64.zip",
                "linux": "https://github.com/littlefs-project/littlefs/releases/download/v2.5.0/mklittlefs-2.5.0-linux-amd64.tar.gz",
                "darwin": "https://github.com/littlefs-project/littlefs/releases/download/v2.5.0/mklittlefs-2.5.0-darwin-amd64.tar.gz"
            }
        }
        
        installed_tools = []
        
        for tool_name, urls in tool_urls.items():
            tool_dir = tools_dir / tool_name
            tool_dir.mkdir(exist_ok=True)
            
            # Check if already installed
            if system == "windows":
                exe_path = tool_dir / f"{tool_name}.exe"
            else:
                exe_path = tool_dir / tool_name
            
            if exe_path.exists():
                installed_tools.append(tool_name)
                continue
            
            # Download tool
            url = urls.get(system, urls.get("linux"))  # Default to Linux if platform not found
            if not url:
                continue
            
            print(f"Downloading {tool_name}...")
            temp_file = tools_dir / f"{tool_name}_temp.zip"
            
            try:
                urllib.request.urlretrieve(url, temp_file)
                
                # Extract tool
                if system == "windows":
                    with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                        zip_ref.extractall(tool_dir)
                        # Find the actual executable in the extracted files
                        for extracted_file in tool_dir.rglob("*.exe"):
                            if tool_name in extracted_file.name.lower():
                                # Move to the expected location
                                extracted_file.rename(exe_path)
                                break
                else:
                    # For Linux/Mac, we'd need tar.gz handling
                    # For now, just create a placeholder
                    with open(exe_path, 'w') as f:
                        f.write("#!/bin/bash\necho 'Tool not yet implemented for this platform'")
                    os.chmod(exe_path, 0o755)
                
                # Clean up temp file
                temp_file.unlink()
                installed_tools.append(tool_name)
                
            except Exception as e:
                print(f"Failed to download {tool_name}: {e}")
                continue
        
        if installed_tools:
            # Add tools directory to PATH
            tools_path = str(tools_dir)
            if tools_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = tools_path + os.pathsep + os.environ.get('PATH', '')
            
            return True, f"Successfully installed: {', '.join(installed_tools)}"
        else:
            return False, "Failed to install any filesystem tools"
            
    except Exception as e:
        return False, f"Error installing filesystem tools: {str(e)}"

def find_fs_builder() -> Optional[str]:
    """Find a file system image builder with automatic installation fallback"""
    # Try to find existing tools first
    if check_command_available("mkspiffs"):
        return "mkspiffs"
    
    if check_command_available("mklittlefs"):
        return "mklittlefs"
    
    # Try to find tools in our custom directory
    tools_dir = Path.home() / ".jtech_uploader" / "tools"
    if tools_dir.exists():
        for tool_name in ["mkspiffs", "mklittlefs"]:
            if platform.system().lower() == "windows":
                tool_path = tools_dir / tool_name / f"{tool_name}.exe"
            else:
                tool_path = tools_dir / tool_name / tool_name
            
            if tool_path.exists() and os.access(tool_path, os.X_OK):
                return str(tool_path)
    
    # If no tools found, try to install them automatically
    print("No filesystem tools found. Attempting automatic installation...")
    success, message = download_and_install_fs_tools()
    
    if success:
        print(f"✅ {message}")
        # Try to find the newly installed tools
        return find_fs_builder()
    else:
        print(f"❌ {message}")
        return None

def get_available_tools() -> Dict[str, bool]:
    """Get a dictionary of available flashing tools for all 25 IC families"""
    return {
        # ESP Series
        "esptool": find_esptool() is not None,
        
        # AVR Series
        "avrdude": find_avrdude() is not None,
        
        # STM32 Series
        "stm32flash": find_stm32flash() is not None,
        
        # PIC Series
        "mplab_ipe": find_mplab_ipe() is not None,
        
        # RP2040 Series
        "rp2040": find_rp2040_tool() is not None,
        
        # Arduino Variants
        "arduino_cli": find_arduino_cli() is not None,
        
        # Teensy Series
        "teensy_loader": find_teensy_loader() is not None,
        
        # MSP430 Series
        "mspdebug": find_mspdebug() is not None,
        
        # EFM32 Series
        "commander": find_commander() is not None,
        
        # LPC Series
        "lpc21isp": find_lpc21isp() is not None,
        
        # Utility Tools
        "hex_converter": find_hex_converter() is not None,
        "fs_builder": find_fs_builder() is not None
    }

def convert_hex_to_bin(hex_file_path: str) -> Tuple[bool, str, str]:
    """
    Convert HEX file to BIN format
    Returns: (success, output_path, error_message)
    """
    try:
        if not os.path.exists(hex_file_path):
            return False, "", "HEX file does not exist"
        
        # Find converter tool
        converter = find_hex_converter()
        if not converter:
            return False, "", "No HEX to BIN converter found. Install srec_cat, objcopy, or hex2bin"
        
        # Create output path
        output_path = os.path.splitext(hex_file_path)[0] + ".bin"
        
        # Run conversion
        if converter == "srec_cat":
            cmd = ["srec_cat", hex_file_path, "-Intel", "-o", output_path, "-Binary"]
        elif converter == "objcopy":
            cmd = ["objcopy", "-I", "ihex", "-O", "binary", hex_file_path, output_path]
        elif converter == "hex2bin":
            cmd = ["hex2bin", hex_file_path]
            output_path = os.path.splitext(hex_file_path)[0] + ".bin"
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True, output_path, f"Successfully converted to {os.path.basename(output_path)}"
        else:
            error_msg = result.stderr or result.stdout or "Unknown conversion error"
            return False, "", f"Conversion failed: {error_msg}"
            
    except Exception as e:
        return False, "", f"Conversion error: {str(e)}"

def create_fs_image(dat_file_path: str, fs_size_mb: int = 1) -> Tuple[bool, str, str]:
    """
    Create a file system image from DAT file
    Returns: (success, output_path, error_message)
    """
    try:
        if not os.path.exists(dat_file_path):
            return False, "", "DAT file does not exist"
        
        # Find FS builder tool
        builder = find_fs_builder()
        if not builder:
            return False, "", "No file system builder found. Install mkspiffs or mklittlefs"
        
        # Create temporary directory structure
        temp_dir = tempfile.mkdtemp(prefix="fs_build_")
        fs_root = os.path.join(temp_dir, "fsroot")
        os.makedirs(fs_root, exist_ok=True)
        
        # Copy DAT file to fsroot
        dat_filename = os.path.basename(dat_file_path)
        fs_dat_path = os.path.join(fs_root, dat_filename)
        shutil.copy2(dat_file_path, fs_dat_path)
        
        # Create output path
        output_path = os.path.splitext(dat_file_path)[0] + "_fs.img"
        fs_size_bytes = fs_size_mb * 1024 * 1024
        
        # Build FS image
        if "mkspiffs" in builder.lower():
            cmd = [builder, "-c", fs_root, "-b", "4096", "-p", "256", "-s", str(fs_size_bytes), output_path]
        elif "mklittlefs" in builder.lower():
            cmd = [builder, "-c", fs_root, "-b", "4096", "-p", "256", "-s", str(fs_size_bytes), output_path]
        else:
            # Fallback for other tools
            cmd = [builder, "-c", fs_root, "-b", "4096", "-p", "256", "-s", str(fs_size_bytes), output_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Cleanup temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True, output_path, f"Successfully created FS image: {os.path.basename(output_path)}"
        else:
            error_msg = result.stderr or result.stdout or "Unknown FS creation error"
            return False, "", f"FS image creation failed: {error_msg}"
            
    except Exception as e:
        return False, "", f"FS image creation error: {str(e)}"

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
        
        # Additional validation for ESP devices
        if file_ext == ".hex":
            # Check if converter is available
            if not find_hex_converter():
                return False, "HEX files require a converter tool (srec_cat, objcopy, or hex2bin). Install one to continue."
        
        if file_ext == ".dat":
            # Check if FS builder is available
            if not find_fs_builder():
                return False, "DAT files require a file system builder (mkspiffs or mklittlefs). Install one to continue."
            
        elif file_ext == ".bin":
            # Check if it's a valid ESP binary (basic size check)
            if file_size < 1024:  # Less than 1KB is suspicious
                return False, "Binary file seems too small for ESP firmware (< 1KB)"
            elif file_size > 16 * 1024 * 1024:  # More than 16MB is suspicious
                return False, "Binary file seems too large for ESP firmware (> 16MB)"
                
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

def get_file_type_info(file_path: str) -> Dict[str, str]:
    """Get detailed information about file type and processing requirements"""
    if not os.path.exists(file_path):
        return {"type": "unknown", "status": "file_not_found"}
    
    file_ext = os.path.splitext(file_path)[1].lower()
    file_size = os.path.getsize(file_path)
    
    info = {
        "extension": file_ext,
        "size_bytes": file_size,
        "size_human": format_file_size(file_size),
        "type": "unknown",
        "status": "unknown",
        "processing_required": False,
        "processing_tool": None,
        "output_format": None,
        "notes": []
    }
    
    if file_ext == ".bin":
        info["type"] = "binary_firmware"
        info["status"] = "ready_to_flash"
        info["processing_required"] = False
        info["output_format"] = "direct_flash"
        
    elif file_ext == ".hex":
        info["type"] = "intel_hex"
        info["status"] = "needs_conversion"
        info["processing_required"] = True
        info["processing_tool"] = find_hex_converter()
        info["output_format"] = "binary"
        
        if info["processing_tool"]:
            info["status"] = "can_convert"
            info["notes"].append(f"Will convert to .bin using {info['processing_tool']}")
        else:
            info["status"] = "converter_missing"
            info["notes"].append("No HEX converter tool found")
            
    elif file_ext == ".dat":
        info["type"] = "data_file"
        info["status"] = "needs_fs_image"
        info["processing_required"] = True
        info["processing_tool"] = find_fs_builder()
        info["output_format"] = "filesystem_image"
        
        if info["processing_tool"]:
            info["status"] = "can_create_fs"
            info["notes"].append(f"Will create FS image using {info['processing_tool']}")
        else:
            info["status"] = "fs_builder_missing"
            info["notes"].append("No file system builder tool found")
    
    elif file_ext == ".uf2":
        info["type"] = "uf2_firmware"
        info["status"] = "ready_to_flash"
        info["processing_required"] = False
        info["output_format"] = "direct_flash"
        info["notes"].append("UF2 format - ready for RP2040, Arduino Nano RP2040, and Teensy devices")
    
    elif file_ext == ".elf":
        info["type"] = "elf_debug"
        info["status"] = "needs_conversion"
        info["processing_required"] = True
        info["processing_tool"] = find_hex_converter()
        info["output_format"] = "binary"
        
        if info["processing_tool"]:
            info["status"] = "can_convert"
            info["notes"].append(f"Will convert ELF to binary using {info['processing_tool']}")
        else:
            info["status"] = "converter_missing"
            info["notes"].append("No ELF converter tool found")
    
    return info

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
    """Create alternating columns pattern for 8x8 LED matrix"""
    pattern = bytearray()
    for y in range(8):
        for x in range(8):
            if x % 2 == 0:
                pattern.extend([255, 0, 0])  # Red
            else:
                pattern.extend([0, 0, 255])  # Blue
    return pattern

def create_checkerboard_pattern():
    """Create checkerboard pattern for 8x8 LED matrix"""
    pattern = bytearray()
    for y in range(8):
        for x in range(8):
            if (x + y) % 2 == 0:
                pattern.extend([255, 255, 255])  # White
            else:
                pattern.extend([0, 0, 0])  # Black
    return pattern

def create_rainbow_pattern():
    """Create rainbow pattern for 8x8 LED matrix"""
    pattern = bytearray()
    for y in range(8):
        for x in range(8):
            # Create rainbow effect
            hue = (x + y) * 32  # 32 steps per color
            if hue < 256:
                # Red to Green
                pattern.extend([255 - hue, hue, 0])
            elif hue < 512:
                # Green to Blue
                pattern.extend([0, 255 - (hue - 256), hue - 256])
            else:
                # Blue to Red
                pattern.extend([hue - 512, 0, 255 - (hue - 512)])
    return pattern

def create_pulse_pattern():
    """Create pulsing pattern for 8x8 LED matrix"""
    pattern = bytearray()
    center_x, center_y = 4, 4
    for y in range(8):
        for x in range(8):
            # Calculate distance from center
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            # Create pulsing effect
            intensity = max(0, 255 - int(distance * 40))
            pattern.extend([intensity, intensity, intensity])
    return pattern

def create_spiral_pattern():
    """Create spiral pattern for 8x8 LED matrix"""
    pattern = bytearray()
    # Create spiral coordinates
    spiral_coords = []
    x, y = 0, 0
    dx, dy = 1, 0
    for i in range(64):
        spiral_coords.append((x, y))
        if (x + dx < 0 or x + dx >= 8 or y + dy < 0 or y + dy >= 8 or 
            (x + dx, y + dy) in spiral_coords):
            # Turn right
            dx, dy = -dy, dx
        x, y = x + dx, y + dy
    
    # Fill pattern with rainbow colors
    for i, (x, y) in enumerate(spiral_coords):
        hue = i * 4  # 4 steps per LED
        if hue < 256:
            pattern.extend([255 - hue, hue, 0])
        elif hue < 512:
            pattern.extend([0, 255 - (hue - 256), hue - 256])
        else:
            pattern.extend([hue - 512, 0, 255 - (hue - 512)])
    
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
