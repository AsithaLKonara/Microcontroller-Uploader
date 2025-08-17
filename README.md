# J Tech Pixel Uploader 🚀

**Professional Firmware Uploader for Microcontrollers with Advanced LED Pattern Support**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)]()

## 🌟 Overview

J Tech Pixel Uploader is a comprehensive, professional-grade firmware uploader designed specifically for microcontroller development and LED matrix projects. Built with Python and Tkinter, it provides an intuitive interface for uploading firmware to various microcontroller platforms while offering advanced features for LED pattern management and device testing.

## ✨ Key Features

### 🔧 Core Functionality
- **Multi-Platform Support**: ESP8266, ESP32, AVR, STM32, PIC microcontrollers
- **Universal File Support**: `.bin`, `.hex`, `.dat` (LED pattern data), and other firmware formats
- **Smart Device Detection**: Automatic COM port detection and device identification
- **Advanced Upload Protocols**: Support for esptool, avrdude, and custom upload methods

### 🎨 LED Pattern Management
- **Real-time Pattern Preview**: Visualize LED patterns before upload
- **Pattern Testing**: Test patterns on hardware before deployment
- **Animation Support**: Create and preview animated LED sequences
- **Pattern Library**: Built-in sample patterns and custom pattern creation
- **Export/Import**: Save and load patterns in `.dat` format

### 🚀 Advanced Features
- **Enhanced Error Handling**: Intelligent error detection with recovery suggestions
- **Progress Tracking**: Real-time upload progress with time estimates
- **Upload Validation**: Pre-upload checks for file integrity and compatibility
- **Auto-retry Logic**: Automatic retry for failed uploads with exponential backoff
- **Device Health Monitoring**: Memory status, flash health, and performance metrics

### 🎯 Modern UI/UX
- **Professional Interface**: Clean, modern design with intuitive navigation
- **Theme Support**: Light, dark, and custom theme options
- **Responsive Layout**: Adaptive design for different screen sizes
- **Keyboard Shortcuts**: Power user shortcuts for efficient operation
- **Drag & Drop**: Easy file management with drag and drop support

### 📊 Monitoring & Debugging
- **Real-time Monitoring**: Live device status and connection monitoring
- **Comprehensive Logging**: Detailed upload logs with timestamp and error tracking
- **Debug Console**: Integrated debugging tools and console output
- **Performance Profiling**: Upload speed analysis and optimization suggestions

## 🛠️ Installation

### Prerequisites
- **Python 3.8 or higher**
- **Windows 10/11** (Primary platform, Linux/macOS support planned)
- **USB connection** for microcontroller communication

### Quick Install
```bash
# Clone the repository
git clone https://github.com/yourusername/j-tech-pixel-uploader.git
cd j-tech-pixel-uploader

# Install dependencies
pip install -r requirements.txt

# Run the application
python j_tech_pixel_uploader.py
```

### Automatic Dependency Installation
The application automatically detects and installs required dependencies:
- **esptool**: ESP8266/ESP32 firmware upload tool
- **pyserial**: Serial communication library
- **Additional tools**: Automatically installed as needed

## 📱 Usage Guide

### 🚀 Getting Started
1. **Launch Application**: Run `python j_tech_pixel_uploader.py`
2. **Connect Device**: Connect your microcontroller via USB
3. **Select Firmware**: Choose your firmware file (`.bin`, `.hex`, `.dat`)
4. **Configure Settings**: Set device type, COM port, and baud rate
5. **Upload**: Click "Upload Firmware" and monitor progress

### 🎨 LED Pattern Management
1. **Open Pattern Preview**: Click "🎨 Preview Uploaded Pattern"
2. **Select Source**: Choose firmware, device, or `.dat` file
3. **Configure Matrix**: Set width, height, and LED type
4. **Preview & Test**: Visualize patterns and test on hardware
5. **Export**: Save patterns for future use

### 🔧 Advanced Configuration
- **Device Settings**: Customize upload parameters for specific boards
- **Theme Customization**: Choose from light, dark, or custom themes
- **Keyboard Shortcuts**: Use shortcuts for common operations
- **Log Management**: View, save, and analyze upload logs

## 📁 Project Structure

```
MicroControllerUploaderPython/
├── j_tech_pixel_uploader.py    # Main application
├── config.py                    # Configuration and settings
├── utils.py                     # Utility functions
├── modern_ui_styles.py         # Modern UI styling system
├── enhanced_ui_layout.py       # Advanced UI layout management
├── enhanced_features.py         # Enhanced functionality modules
├── enhanced_error_handler.py   # Advanced error handling
├── enhanced_progress_tracker.py # Progress tracking system
├── SampleFirmware/             # Sample firmware and patterns
├── UploadLogs/                 # Upload session logs
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔌 Supported Devices

### ESP Series
- **ESP8266**: NodeMCU, ESP-01, ESP-07, ESP-12E/F
- **ESP32**: ESP32-WROOM, ESP32-WROVER, ESP32-S2, ESP32-C3
- **ESP32-S3**: Latest ESP32 variant with enhanced features

### AVR Series
- **Arduino**: Uno, Nano, Mega, Pro Mini
- **Standalone**: ATmega328P, ATmega2560, ATtiny85

### STM32 Series
- **STM32F1**: Blue Pill, Black Pill
- **STM32F4**: Discovery boards, Nucleo boards

### PIC Series
- **PIC16**: PIC16F877A, PIC16F84A
- **PIC18**: PIC18F4550, PIC18F4620

## 📊 File Format Support

### Firmware Files
- **`.bin`**: Binary firmware files (ESP8266, ESP32)
- **`.hex`**: Intel HEX format (AVR, STM32, PIC)
- **`.dat`**: LED pattern data files (custom format)
- **`.elf`**: ELF format files (debugging and development)

### LED Pattern Files (`.dat`)
- **Format**: Raw RGB byte data
- **Structure**: Width × Height × 3 bytes (R, G, B)
- **Compatibility**: WS2812B, WS2811, SK6812, APA102
- **Features**: Animation support, color transitions, pattern effects

## 🚨 Troubleshooting

### Common Issues

#### Upload Fails
1. **Check Connections**: Ensure proper USB connection
2. **Verify Port**: Confirm correct COM port selection
3. **Device Mode**: Ensure device is in flash mode
4. **Power Supply**: Check if device has sufficient power

#### LED Pixels Not Working
1. **Power Supply**: Ensure adequate 5V power supply
2. **Data Line**: Verify correct GPIO pin connection
3. **Ground Connection**: Ensure common ground between devices
4. **Firmware Compatibility**: Check if firmware supports LED control

#### Connection Issues
1. **Driver Installation**: Install proper USB-to-Serial drivers
2. **Port Permissions**: Check port access permissions
3. **Baud Rate**: Verify correct baud rate settings
4. **Device Reset**: Try manual reset sequence

### Diagnostic Tools
- **Connection Test**: Built-in connection testing
- **Device Health Check**: Comprehensive device diagnostics
- **Error Logs**: Detailed error reporting and solutions
- **Hardware Reset**: Automatic device reset functionality

## 🔧 Configuration

### Application Settings
```python
# config.py - Main configuration file
APP_NAME = "J Tech Pixel Uploader"
APP_VERSION = "2.0.0"
DEFAULT_WINDOW_SIZE = "1200x800"
DEFAULT_DEVICE = "ESP8266"
DEFAULT_BAUD_RATE = "115200"

# Supported devices and configurations
DEVICE_CONFIGS = {
    "ESP8266": {
        "upload_tool": "esptool",
        "baud_rates": ["115200", "57600", "38400", "74880"],
        "flash_mode": "dio",
        "flash_freq": "40m"
    }
    # ... more device configurations
}
```

### Custom Themes
```python
# Theme configuration
UI_THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "accent": "#007acc"
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "accent": "#007acc"
    }
}
```

## 🧪 Testing

### Test Scripts
- **`test_app.py`**: Basic application functionality tests
- **`comprehensive_verification.py`**: Full feature verification
- **`definitive_test.py`**: Final testing and validation
- **`test_pattern_testing.py`**: LED pattern functionality tests

### Sample Firmware
The `SampleFirmware/` directory contains:
- **Test Patterns**: Various LED matrix patterns
- **Sample Firmware**: Example firmware files for testing
- **Pattern Data**: `.dat` files for LED pattern testing

## 📈 Performance

### Upload Speeds
- **ESP8266**: 115200 baud - ~11.5 KB/s
- **ESP32**: 921600 baud - ~92 KB/s
- **AVR**: 57600 baud - ~5.8 KB/s

### Memory Usage
- **Base Application**: ~50 MB RAM
- **With Pattern Preview**: ~75 MB RAM
- **Upload Process**: +10-20 MB RAM

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/j-tech-pixel-uploader.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **esptool**: ESP8266/ESP32 firmware upload tool
- **pyserial**: Cross-platform serial communication library
- **Tkinter**: Python GUI framework
- **Community**: All contributors and users

## 📞 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/yourusername/j-tech-pixel-uploader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/j-tech-pixel-uploader/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/j-tech-pixel-uploader/wiki)

### Contact
- **Email**: support@jtechpixel.com
- **Website**: [jtechpixel.com](https://jtechpixel.com)
- **Discord**: [Join our community](https://discord.gg/jtechpixel)

## 🔄 Changelog

### Version 2.0.0 (Current)
- ✨ Complete UI overhaul with modern 2-column design
- 🎨 Advanced LED pattern preview and management
- 🚀 Enhanced error handling and progress tracking
- 📊 Comprehensive monitoring and debugging tools
- 🎯 Professional-grade interface and user experience
- 📱 Left column: All controls and configuration
- 📝 Right column: Large upload log for better visibility

### Version 1.0.0
- 🚀 Initial release with basic upload functionality
- 🔧 Support for ESP8266, ESP32, AVR, STM32, PIC
- 📁 Multiple file format support
- 🔌 Basic device detection and connection

---

**Made with ❤️ by J Tech Pixel Team**

*Empowering makers and developers with professional microcontroller tools*