# 🔧 Automatic Dependency Installer

The J Tech Pixel Uploader now includes an **automatic dependency checker and installer** that runs when the software starts. This eliminates the need for manual setup and ensures all required packages are available.

## 🚀 How It Works

### 1. **Automatic Detection**
When you start the software, it automatically checks for:
- **Required Python packages**: `pyserial`, `esptool`
- **Optional system tools**: `avrdude`, `stm32flash`, `MPLAB IPE`

### 2. **Smart Installation**
If dependencies are missing:
- A user-friendly dialog appears
- Click "Install Dependencies" to automatically install via pip
- Progress bar shows installation status
- Automatic restart after successful installation

### 3. **Real-time Status**
- Dependency status is displayed in the application log
- Clear indicators for missing vs. available packages
- Helpful messages for manual installation if needed

## 📦 Required Dependencies

### **Core Python Packages**
- **`pyserial`** - Serial communication with microcontrollers
- **`esptool`** - ESP8266/ESP32 firmware flashing

### **Optional System Tools**
- **`avrdude`** - Arduino/AVR programming support
- **`stm32flash`** - STM32 programming support
- **`MPLAB IPE`** - PIC microcontroller support

## 🎯 Installation Process

### **Automatic Installation (Recommended)**
1. Start the J Tech Pixel Uploader
2. If dependencies are missing, a dialog appears
3. Click "Install Dependencies"
4. Wait for installation to complete
5. Application automatically restarts
6. All features are now available!

### **Manual Installation (Alternative)**
If automatic installation fails, install manually:

```bash
# Install required Python packages
pip install pyserial esptool

# For Windows users
python -m pip install pyserial esptool
```

## 🧪 Testing Dependencies

### **Test Script**
Run the included test script to check dependency status:

```bash
# Windows
test_dependencies.bat

# PowerShell
test_dependencies.ps1

# Direct Python
python test_dependency_checker.py
```

### **What the Test Shows**
- ✅ Available packages
- ❌ Missing packages
- 🔧 System tool status
- 💡 Installation instructions

## 🔍 How Dependency Checking Works

### **Python Package Detection**
```python
def check_package_available(package_name):
    try:
        importlib.util.find_spec(package_name)
        return True
    except ImportError:
        return False
```

### **System Tool Detection**
```python
def check_esptool_available():
    # Try import first
    if importlib.util.find_spec('esptool'):
        return True
    
    # Try command execution
    result = subprocess.run(['python', '-m', 'esptool', '--help'])
    return result.returncode == 0
```

## 🎨 User Interface Features

### **Dependency Installer Dialog**
- **Professional Design** - Matches main application theme
- **Progress Tracking** - Real-time installation status
- **Error Handling** - Clear error messages and solutions
- **Manual Instructions** - Fallback installation commands

### **Status Display**
- **Color-coded Logs** - Green for success, yellow for warnings
- **Emoji Indicators** - Visual status indicators
- **Detailed Messages** - Clear explanations of what's happening

## 🚨 Troubleshooting

### **Common Issues**

#### **Installation Fails**
- Check internet connection
- Verify Python and pip are properly installed
- Try running as administrator (Windows)
- Check firewall/antivirus settings

#### **Permission Errors**
```bash
# Windows - Run as Administrator
# Linux/macOS - Use sudo if needed
sudo pip install pyserial esptool
```

#### **Python Path Issues**
```bash
# Verify Python installation
python --version
pip --version

# Use specific Python version
python3 -m pip install pyserial esptool
```

### **Manual Recovery**
If automatic installation completely fails:

1. **Close the application**
2. **Open command prompt/terminal**
3. **Install manually:**
   ```bash
   pip install pyserial esptool
   ```
4. **Restart the application**

## 🔧 Advanced Configuration

### **Custom Installation Commands**
You can modify the installation commands in `main.py`:

```python
# Default installation
cmd = [sys.executable, '-m', 'pip', 'install', package]

# Custom pip location
cmd = ['/path/to/pip', 'install', package]

# With specific version
cmd = [sys.executable, '-m', 'pip', 'install', f'{package}==1.2.3']
```

### **Additional Dependencies**
To add more dependencies, modify the `check_and_install_dependencies` method:

```python
# Add new package check
if not self.check_package_available('new_package'):
    missing_packages.append('new_package')
```

## 📋 System Requirements

### **Operating Systems**
- ✅ **Windows 10/11** (Primary target)
- ✅ **Linux** (Ubuntu, Debian, CentOS)
- ✅ **macOS** (10.14+)

### **Python Versions**
- ✅ **Python 3.6+** (Required)
- ✅ **Python 3.8+** (Recommended)
- ✅ **Python 3.11+** (Latest features)

### **Hardware**
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB free space
- **USB**: USB 2.0+ for microcontroller connection

## 🎉 Benefits

### **For Users**
- **Zero Setup** - Just run and go!
- **Automatic Updates** - Dependencies stay current
- **Clear Feedback** - Know exactly what's happening
- **Professional Experience** - No technical knowledge required

### **For Developers**
- **Reduced Support** - Fewer "it won't run" issues
- **Better UX** - Smooth user experience
- **Maintainable Code** - Centralized dependency management
- **Error Handling** - Robust failure recovery

## 🔮 Future Enhancements

### **Planned Features**
- **Version Management** - Install specific package versions
- **Dependency Updates** - Check for newer versions
- **Offline Installation** - Bundle dependencies with installer
- **Custom Sources** - Support for private package repositories

### **Integration Ideas**
- **Package Manager Detection** - Use conda, poetry, etc.
- **Virtual Environment Support** - Auto-create isolated environments
- **Dependency Locking** - Ensure reproducible builds
- **Health Checks** - Regular dependency validation

---

## 📞 Support

If you encounter issues with the dependency installer:

1. **Check the logs** in the application
2. **Run the test script** to diagnose issues
3. **Review this documentation** for solutions
4. **Contact support** with specific error messages

The automatic dependency installer makes the J Tech Pixel Uploader truly user-friendly and professional! 🚀
