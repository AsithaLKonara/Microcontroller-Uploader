import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import serial
import serial.tools.list_ports
import os
import threading
import subprocess
import time
from datetime import datetime
import utils
import config
import sys
import importlib.util
from PIL import Image, ImageTk, ImageDraw
import numpy as np

class JTechPixelUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("J Tech Pixel Uploader v3.0 - Multi-IC LED Matrix Flasher")
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
        
        # Check and install dependencies after colors are initialized
        self.check_and_install_dependencies()

        
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
        self.log_success("🚀 J Tech Pixel Uploader v3.0 Started")
        self.log_message("💡 Select a firmware file and configure your device to begin")
        
        # Show dependency status
        self.show_dependency_status()
        
        # Apply initial responsive adjustments
        self.apply_initial_responsive_settings()
        
    def check_and_install_dependencies(self):
        """Check and automatically install required dependencies"""
        try:
            # Check if required packages are available
            missing_packages = []
            dependency_errors = []
            
            # Check pyserial
            if not self.check_package_available('serial'):
                missing_packages.append('pyserial')
                dependency_errors.append("❌ pyserial package not found - Serial communication will not work")
            else:
                dependency_errors.append("✅ pyserial package available")
            
            # Check esptool
            if not self.check_esptool_available():
                missing_packages.append('esptool')
                dependency_errors.append("❌ esptool package not found - ESP8266/ESP32 flashing will not work")
            else:
                dependency_errors.append("✅ esptool package available")
            
            # If packages are missing, show installation dialog
            if missing_packages:
                # Only show installer if colors are available (UI is initialized)
                if hasattr(self, 'colors'):
                    self.show_dependency_installer(missing_packages)
                else:
                    print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
                    print("💡 Install with: pip install " + " ".join(missing_packages))
                
                # Log dependency errors to the uploader log
                if hasattr(self, 'log_error'):
                    for error in dependency_errors:
                        if "❌" in error:
                            self.log_error(error)
                        else:
                            self.log_message(error)
            else:
                print("✅ All required Python dependencies are available")
                # Log success to uploader log
                if hasattr(self, 'log_success'):
                    self.log_success("✅ All required Python dependencies are available")
                
            # Check system tools (optional but recommended)
            if hasattr(self, 'colors'):
                system_tool_errors = self.check_system_tools()
                if system_tool_errors:
                    for tool_error in system_tool_errors:
                        if hasattr(self, 'log_warning'):
                            self.log_warning(tool_error)
                
        except Exception as e:
            error_msg = f"⚠️ Error checking dependencies: {e}"
            print(error_msg)
            # Log error to uploader log if available
            if hasattr(self, 'log_error'):
                self.log_error(error_msg)
    
    def check_package_available(self, package_name):
        """Check if a Python package is available"""
        try:
            importlib.util.find_spec(package_name)
            return True
        except ImportError:
            return False
    
    def check_esptool_available(self):
        """Check if esptool is available"""
        try:
            # Try to import esptool
            importlib.util.find_spec('esptool')
            return True
        except ImportError:
            # Try to run esptool command
            try:
                result = subprocess.run(['python', '-m', 'esptool', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except:
                return False
    
    def show_dependency_installer(self, missing_packages):
        """Show dependency installation dialog"""
        # Log to main log that dependency installer is being shown
        if hasattr(self, 'log_error'):
            self.log_error("🚨 DEPENDENCY INSTALLER REQUIRED")
            self.log_error(f"❌ Missing packages: {', '.join(missing_packages)}")
            self.log_message("💡 Dependency installer dialog will open")
            self.log_message("🔧 Click 'Install Dependencies' to fix automatically")
        
        # Create a new window for dependency installation
        self.dep_window = tk.Toplevel(self.root)
        self.dep_window.title("Dependency Installation Required")
        self.dep_window.geometry("500x400")
        self.dep_window.configure(bg=self.colors['background'])
        self.dep_window.resizable(False, False)
        self.dep_window.transient(self.root)
        self.dep_window.grab_set()
        
        # Center the window
        self.dep_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 250,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 200))
        
        # Main frame
        main_frame = ttk.Frame(self.dep_window, style='Card.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🔧 Missing Dependencies Detected", 
                               style='Title.TLabel')
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="The following required packages are not installed:",
                              style='Subtitle.TLabel')
        desc_label.pack(pady=(0, 20))
        
        # Missing packages list
        packages_frame = ttk.Frame(main_frame)
        packages_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        for package in missing_packages:
            pkg_label = ttk.Label(main_frame, 
                                 text=f"• {package}", 
                                 style='Section.TLabel')
            pkg_label.pack(anchor='w', pady=2)
        
        # Installation info
        info_label = ttk.Label(main_frame, 
                              text="Click 'Install Dependencies' to automatically install them via pip",
                              style='Subtitle.TLabel')
        info_label.pack(pady=(0, 20))
        
        # Progress bar
        self.install_progress = ttk.Progressbar(main_frame, 
                                               style='Custom.Horizontal.TProgressbar',
                                               mode='indeterminate')
        self.install_progress.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status label
        self.install_status = ttk.Label(main_frame, 
                                       text="Ready to install", 
                                       style='Status.TLabel')
        self.install_status.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Install button
        install_btn = ttk.Button(buttons_frame, 
                                text="Install Dependencies", 
                                style='Primary.TButton',
                                command=lambda: self.install_dependencies(missing_packages))
        install_btn.pack(side='left', padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, 
                               text="Cancel", 
                               style='Secondary.TButton',
                               command=self.dep_window.destroy)
        cancel_btn.pack(side='left')
        
        # Manual install info
        manual_info = ttk.Label(main_frame, 
                               text="Or install manually: pip install " + " ".join(missing_packages),
                               style='FileInfo.TLabel')
        manual_info.pack(pady=(20, 0))
    
    def install_dependencies(self, packages):
        """Install missing dependencies using pip"""
        def install_thread():
            try:
                # Log installation start to main log
                if hasattr(self, 'log_progress'):
                    self.log_progress("🚀 Starting dependency installation...")
                    self.log_progress(f"📦 Installing packages: {', '.join(packages)}")
                
                self.install_status.config(text="Installing dependencies...")
                self.install_progress.start()
                
                for package in packages:
                    # Log package installation start
                    if hasattr(self, 'log_progress'):
                        self.log_progress(f"📦 Installing {package}...")
                    
                    self.install_status.config(text=f"Installing {package}...")
                    
                    # Install package using pip
                    cmd = [sys.executable, '-m', 'pip', 'install', package]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if result.returncode != 0:
                        error_msg = f"Failed to install {package}: {result.stderr}"
                        # Log error to main log
                        if hasattr(self, 'log_error'):
                            self.log_error(f"❌ {error_msg}")
                        raise Exception(error_msg)
                    
                    # Log successful installation
                    if hasattr(self, 'log_success'):
                        self.log_success(f"✅ Successfully installed {package}")
                    print(f"✅ Successfully installed {package}")
                
                # Log installation completion
                if hasattr(self, 'log_success'):
                    self.log_success("🎉 All dependencies installed successfully!")
                    self.log_progress("🔄 Application will restart to load new packages...")
                
                self.install_status.config(text="Installation completed successfully!")
                self.install_progress.stop()
                
                # Show success message and close window
                messagebox.showinfo("Success", 
                                  "All dependencies have been installed successfully!\n"
                                  "The application will now restart to load the new packages.")
                
                # Restart the application
                self.root.after(2000, self.restart_application)
                
            except Exception as e:
                # Log installation failure to main log
                if hasattr(self, 'log_error'):
                    self.log_error(f"❌ Dependency installation failed: {str(e)}")
                    self.log_message("🔧 Please install manually using: pip install " + " ".join(packages))
                
                self.install_progress.stop()
                self.install_status.config(text=f"Installation failed: {str(e)}")
                messagebox.showerror("Installation Error", 
                                   f"Failed to install dependencies:\n{str(e)}\n\n"
                                   f"Please install manually using:\npip install {' '.join(packages)}")
                print(f"❌ Dependency installation failed: {e}")
        
        # Run installation in separate thread
        threading.Thread(target=install_thread, daemon=True).start()
    
    def restart_application(self):
        """Restart the application to load newly installed packages"""
        try:
            # Close current window
            self.root.destroy()
            
            # Restart the application
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"❌ Failed to restart application: {e}")
            messagebox.showwarning("Restart Required", 
                                 "Please manually restart the application to load the new packages.")
    
    def check_system_tools(self):
        """Check if required system tools are available"""
        missing_tools = []
        tool_errors = []
        
        # Check for esptool (ESP series)
        if not self.check_esptool_available():
            missing_tools.append("esptool")
            tool_errors.append("⚠️ esptool system tool not found - ESP8266/ESP32/ESP32-S3/ESP32-C6/ESP32-H2 flashing may not work properly")
        else:
            tool_errors.append("✅ esptool system tool available - Full ESP series support")
        
        # Check for avrdude (AVR series)
        try:
            result = subprocess.run(['avrdude', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("avrdude")
                tool_errors.append("⚠️ avrdude not found - AVR/ATtiny/ATmega microcontroller support limited")
            else:
                tool_errors.append("✅ avrdude available - Full AVR series support (Arduino, ATtiny, ATmega)")
        except:
            missing_tools.append("avrdude")
            tool_errors.append("⚠️ avrdude not found - AVR/ATtiny/ATmega microcontroller support limited")
        
        # Check for stm32flash (STM32 series)
        try:
            result = subprocess.run(['stm32flash', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("stm32flash")
                tool_errors.append("⚠️ stm32flash not found - STM32 series support limited")
            else:
                tool_errors.append("✅ stm32flash available - Full STM32 series support (F1/F4/F7/H7/L4/G0)")
        except:
            missing_tools.append("stm32flash")
            tool_errors.append("⚠️ stm32flash not found - STM32 series support limited")
        
        # Check for rp2040 (Raspberry Pi Pico)
        try:
            result = subprocess.run(['python', '-m', 'rp2040', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("rp2040")
                tool_errors.append("⚠️ rp2040 tool not found - Raspberry Pi Pico support limited")
            else:
                tool_errors.append("✅ rp2040 tool available - Raspberry Pi Pico support")
        except:
            missing_tools.append("rp2040")
            tool_errors.append("⚠️ rp2040 tool not found - Raspberry Pi Pico support limited")
        
        # Check for arduino-cli (Arduino variants)
        try:
            result = subprocess.run(['arduino-cli', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("arduino-cli")
                tool_errors.append("⚠️ arduino-cli not found - Arduino Nano 33 BLE/RP2040 support limited")
            else:
                tool_errors.append("✅ arduino-cli available - Arduino variants support")
        except:
            missing_tools.append("arduino-cli")
            tool_errors.append("⚠️ arduino-cli not found - Arduino Nano 33 BLE/RP2040 support limited")
        
        # Check for teensy_loader_cli (Teensy series)
        try:
            result = subprocess.run(['teensy_loader_cli', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("teensy_loader_cli")
                tool_errors.append("⚠️ teensy_loader_cli not found - Teensy series support limited")
            else:
                tool_errors.append("✅ teensy_loader_cli available - Teensy series support")
        except:
            missing_tools.append("teensy_loader_cli")
            tool_errors.append("⚠️ teensy_loader_cli not found - Teensy series support limited")
        
        # Check for mspdebug (MSP430)
        try:
            result = subprocess.run(['mspdebug', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("mspdebug")
                tool_errors.append("⚠️ mspdebug not found - MSP430 support limited")
            else:
                tool_errors.append("✅ mspdebug available - MSP430 support")
        except:
            missing_tools.append("mspdebug")
            tool_errors.append("⚠️ mspdebug not found - MSP430 support limited")
        
        # Check for commander (EFM32)
        try:
            result = subprocess.run(['commander', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("commander")
                tool_errors.append("⚠️ commander not found - EFM32 support limited")
            else:
                tool_errors.append("✅ commander available - EFM32 support")
        except:
            missing_tools.append("commander")
            tool_errors.append("⚠️ commander not found - EFM32 support limited")
        
        # Check for lpc21isp (LPC)
        try:
            result = subprocess.run(['lpc21isp', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_tools.append("lpc21isp")
                tool_errors.append("⚠️ lpc21isp not found - LPC support limited")
            else:
                tool_errors.append("✅ lpc21isp available - LPC support")
        except:
            missing_tools.append("lpc21isp")
            tool_errors.append("⚠️ lpc21isp not found - LPC support limited")
        
        # Log detailed tool status
        if hasattr(self, 'log_message'):
            for tool_status in tool_errors:
                if "⚠️" in tool_status:
                    self.log_warning(tool_status)
                else:
                    self.log_message(tool_status)
        
        if missing_tools:
            if hasattr(self, 'log_warning'):
                self.log_warning(f"⚠️ Some system tools are missing: {', '.join(missing_tools)}")
                self.log_message("💡 These tools are optional but provide additional microcontroller support")
                self.log_message("📥 Install them manually or use the dependency installer for Python packages")
        
        return tool_errors
    
    def show_dependency_status(self):
        """Show a summary of dependency status in the log"""
        try:
            self.log_system("🔍 Checking dependency status...")
            
            # Check Python packages
            pyserial_ok = self.check_package_available('serial')
            esptool_ok = self.check_esptool_available()
            
            if pyserial_ok and esptool_ok:
                self.log_success("✅ All required Python packages are available")
                self.log_message("📦 pyserial: Available for serial communication")
                self.log_message("📦 esptool: Available for ESP8266/ESP32 flashing")
            else:
                missing = []
                if not pyserial_ok:
                    missing.append("pyserial")
                    self.log_error("❌ pyserial missing - Serial communication will not work")
                if not esptool_ok:
                    missing.append("esptool")
                    self.log_error("❌ esptool missing - ESP8266/ESP32 flashing will not work")
                
                self.log_warning(f"⚠️ Missing Python packages: {', '.join(missing)}")
                self.log_message("💡 Use the dependency installer to install missing packages")
                self.log_message("🔧 Manual installation: pip install " + " ".join(missing))
            
            # Check system tools
            if hasattr(self, 'colors'):
                self.log_system("🔍 Checking system tools...")
                system_tool_errors = self.check_system_tools()
                
                # Count available vs missing tools
                available_tools = sum(1 for error in system_tool_errors if "✅" in error)
                missing_tools = sum(1 for error in system_tool_errors if "⚠️" in error)
                
                if missing_tools == 0:
                    self.log_success("✅ All system tools are available")
                else:
                    self.log_warning(f"⚠️ {missing_tools} system tool(s) missing")
                    self.log_message("💡 These are optional but provide enhanced microcontroller support")
                    self.log_message("📥 Install them manually for full functionality")
                
                self.log_system(f"📊 System tools: {available_tools} available, {missing_tools} missing")
                
        except Exception as e:
            self.log_warning(f"⚠️ Could not verify dependency status: {e}")
            self.log_error(f"🔧 Dependency check error: {str(e)}")
    
    def manual_dependency_check(self):
        """Manual dependency check triggered by user"""
        try:
            self.log_system("🔍 Manual dependency check initiated...")
            self.log_message("📋 Checking all dependencies and system tools...")
            
            # Clear previous dependency messages
            self.log_system("=" * 50)
            self.log_system("DEPENDENCY STATUS REPORT")
            self.log_system("=" * 50)
            
            # Run comprehensive dependency check
            self.show_dependency_status()
            
            # Add summary and recommendations
            self.log_system("=" * 50)
            self.log_system("RECOMMENDATIONS")
            self.log_system("=" * 50)
            
            # Check if we have critical dependencies
            pyserial_ok = self.check_package_available('serial')
            esptool_ok = self.check_esptool_available()
            
            if not pyserial_ok or not esptool_ok:
                self.log_error("🚨 CRITICAL: Missing required dependencies!")
                self.log_message("💡 Use the dependency installer to fix this")
                self.log_message("🔧 Or install manually: pip install pyserial esptool")
            else:
                self.log_success("✅ All critical dependencies are available")
                self.log_message("🚀 Ready for firmware uploads!")
            
            # Show detailed dependency report
            self.show_detailed_dependency_report()
            
            self.log_system("=" * 50)
            self.log_system("Dependency check complete")
            self.log_system("=" * 50)
            
        except Exception as e:
            self.log_error(f"❌ Dependency check failed: {str(e)}")
            self.log_message("🔧 Please check the error details above")
    
    def show_detailed_dependency_report(self):
        """Show detailed dependency report in the log"""
        try:
            self.log_system("📊 DETAILED DEPENDENCY REPORT")
            self.log_system("-" * 30)
            
            # Python packages
            self.log_system("🐍 PYTHON PACKAGES:")
            pyserial_ok = self.check_package_available('serial')
            esptool_ok = self.check_esptool_available()
            
            if pyserial_ok:
                self.log_success("  ✅ pyserial - Serial communication support")
            else:
                self.log_error("  ❌ pyserial - Serial communication will fail")
            
            if esptool_ok:
                self.log_success("  ✅ esptool - ESP8266/ESP32 flashing support")
            else:
                self.log_error("  ❌ esptool - ESP8266/ESP32 flashing will fail")
            
            # System tools
            self.log_system("🔧 SYSTEM TOOLS:")
            try:
                # Check avrdude
                result = subprocess.run(['avrdude', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ avrdude - AVR series support (Arduino, ATtiny, ATmega)")
                else:
                    self.log_warning("  ⚠️ avrdude - AVR series support limited")
            except:
                self.log_warning("  ⚠️ avrdude - AVR series support limited")
            
            try:
                # Check stm32flash
                result = subprocess.run(['stm32flash', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ stm32flash - STM32 series support (F1/F4/F7/H7/L4/G0)")
                else:
                    self.log_warning("  ⚠️ stm32flash - STM32 series support limited")
            except:
                self.log_warning("  ⚠️ stm32flash - STM32 series support limited")
            
            try:
                # Check rp2040
                result = subprocess.run(['python', '-m', 'rp2040', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ rp2040 - Raspberry Pi Pico support")
                else:
                    self.log_warning("  ⚠️ rp2040 - Raspberry Pi Pico support limited")
            except:
                self.log_warning("  ⚠️ rp2040 - Raspberry Pi Pico support limited")
            
            try:
                # Check arduino-cli
                result = subprocess.run(['arduino-cli', 'version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ arduino-cli - Arduino variants support")
                else:
                    self.log_warning("  ⚠️ arduino-cli - Arduino variants support limited")
            except:
                self.log_warning("  ⚠️ arduino-cli - Arduino variants support limited")
            
            try:
                # Check teensy_loader_cli
                result = subprocess.run(['teensy_loader_cli', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ teensy_loader_cli - Teensy series support")
                else:
                    self.log_warning("  ⚠️ teensy_loader_cli - Teensy series support limited")
            except:
                self.log_warning("  ⚠️ teensy_loader_cli - Teensy series support limited")
            
            try:
                # Check mspdebug
                result = subprocess.run(['mspdebug', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ mspdebug - MSP430 support")
                else:
                    self.log_warning("  ⚠️ mspdebug - MSP430 support limited")
            except:
                self.log_warning("  ⚠️ mspdebug - MSP430 support limited")
            
            try:
                # Check commander
                result = subprocess.run(['commander', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ commander - EFM32 support")
                else:
                    self.log_warning("  ⚠️ commander - EFM32 support limited")
            except:
                self.log_warning("  ⚠️ commander - EFM32 support limited")
            
            try:
                # Check lpc21isp
                result = subprocess.run(['lpc21isp', '--help'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("  ✅ lpc21isp - LPC support")
                else:
                    self.log_warning("  ⚠️ lpc21isp - LPC support limited")
            except:
                self.log_warning("  ⚠️ lpc21isp - LPC support limited")
            
            # Python version and platform info
            self.log_system("💻 SYSTEM INFORMATION:")
            self.log_message(f"  Python: {sys.version.split()[0]}")
            self.log_message(f"  Platform: {sys.platform}")
            self.log_message(f"  Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
            
            # Recommendations
            self.log_system("💡 RECOMMENDATIONS:")
            if not pyserial_ok or not esptool_ok:
                self.log_error("  🚨 Install missing Python packages immediately")
                self.log_message("  💡 Use: pip install pyserial esptool")
            else:
                self.log_success("  ✅ All critical dependencies are available")
                self.log_message("  🚀 You can proceed with firmware uploads")
            
            self.log_message("  💡 System tools (avrdude, stm32flash, rp2040, arduino-cli, teensy_loader_cli, mspdebug, commander, lpc21isp) are optional")
            self.log_message("  💡 They provide enhanced microcontroller support for all 25 IC families")
            
        except Exception as e:
            self.log_error(f"❌ Detailed report generation failed: {str(e)}")
    
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
        ttk.Button(buttons_frame, text="🎨 Pattern Editor", command=self.open_pattern_editor,
                  style='Secondary.TButton').grid(row=0, column=1, padx=(0, 10))
        self.upload_button = ttk.Button(buttons_frame, text="🚀 Upload", command=self.start_upload,
                                       style='Primary.TButton')
        self.upload_button.grid(row=0, column=2)
        
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
                   style='Info.TButton').grid(row=0, column=2, padx=(0, 10))
        ttk.Button(log_controls, text="🔍 Check Dependencies", command=self.manual_dependency_check,
                   style='Info.TButton').grid(row=0, column=3)
        
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
                ("Firmware files", "*.bin *.hex *.dat *.elf *.uf2"),
                ("Binary files", "*.bin"),
                ("Hex files", "*.hex"),
                ("Data files", "*.dat"),
                ("UF2 files", "*.uf2"),
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
        
        # Validation for RP2040 devices
        elif device == "RP2040":
            if file_ext not in [".uf2", ".bin"]:
                self.log_message("⚠ Warning: RP2040 devices prefer .uf2 files for easy flashing")
        
        # Validation for Teensy devices
        elif device.startswith("Teensy"):
            if file_ext not in [".hex", ".bin"]:
                self.log_message("⚠ Warning: Teensy devices support .hex and .bin files")
        
        # Validation for Arduino variants
        elif device.startswith("Arduino-Nano"):
            if file_ext not in [".hex", ".bin", ".uf2"]:
                self.log_message("⚠ Warning: Arduino Nano variants support .hex, .bin, and .uf2 files")
                    
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
                
                # Show special info for RP2040
                elif device == "RP2040":
                    self.log_message("💡 RP2040 devices support .uf2 files for easy drag-and-drop flashing")
                    self.log_message("💡 .bin files are also supported for advanced users")
                
                # Show special info for Teensy devices
                elif device.startswith("Teensy"):
                    self.log_message("💡 Teensy devices support .hex and .bin files")
                    self.log_message("💡 Teensy Loader CLI tool required for flashing")
                
                # Show special info for Arduino variants
                elif device.startswith("Arduino-Nano"):
                    self.log_message("💡 Arduino Nano variants support multiple formats")
                    self.log_message("💡 Arduino CLI tool required for compilation and upload")
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
            ("All supported files", "*.bin;*.hex;*.dat;*.uf2;*.elf"),
            ("Binary files", "*.bin"),
            ("Intel HEX files", "*.hex"),
            ("Data files", "*.dat"),
            ("UF2 files", "*.uf2"),
            ("ELF files", "*.elf"),
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
            elif info.get('type') in ['uf2_firmware', 'elf_debug']:
                self.firmware_mode_var.set("firmware")
                self.log_message("⚙️ Firmware file detected - switching to Firmware Mode")
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
    
    def open_pattern_editor(self):
        """Open the visual pattern editor dialog"""
        try:
            # Get current device for matrix size suggestion
            device = self.selected_device.get()
            matrix_size = (8, 8)  # Default size
            
            # Suggest matrix size based on device
            if device.startswith("ESP"):
                if "32" in device:
                    matrix_size = (16, 16)  # ESP32 can handle larger matrices
                else:
                    matrix_size = (8, 8)  # ESP8266 works well with 8x8
            
            # Open pattern editor
            editor = PatternEditorDialog(self.root, matrix_size)
            self.log_success("🎨 Pattern Editor opened")
            self.log_message("💡 Create custom LED patterns and export as .dat files")
            
        except Exception as e:
            self.log_error(f"Failed to open Pattern Editor: {str(e)}")
            messagebox.showerror("Error", f"Failed to open Pattern Editor:\n{str(e)}")


class PatternEditorDialog:
    """Visual pattern editor for creating and editing LED patterns"""
    
    def __init__(self, parent, matrix_size=(8, 8)):
        self.parent = parent
        self.matrix_size = matrix_size
        self.leds = matrix_size[0] * matrix_size[1]
        self.pattern_data = [[0, 0, 0] for _ in range(self.leds)]  # RGB values
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"🎨 LED Pattern Editor - {matrix_size[0]}x{matrix_size[1]}")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.create_canvas()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Matrix size selector
        size_frame = ttk.Frame(control_frame)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(size_frame, text="Matrix Size:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value=f"{self.matrix_size[0]}x{self.matrix_size[1]}")
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, 
                                 values=["8x8", "16x16", "32x32"], state="readonly")
        size_combo.pack(side=tk.LEFT, padx=(10, 0))
        size_combo.bind("<<ComboboxSelected>>", self.on_size_change)
        
        # Color picker
        color_frame = ttk.Frame(control_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="Current Color:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="#FF0000")
        color_entry = ttk.Entry(color_frame, textvariable=self.color_var, width=10)
        color_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        self.color_button = tk.Button(color_frame, bg="#FF0000", width=3, height=1,
                                    command=self.pick_color)
        self.color_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Tool buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🎨 Pick Color", command=self.pick_color).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ Clear All", command=self.clear_pattern).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Random", command=self.random_pattern).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📁 Import Image", command=self.import_image).pack(side=tk.LEFT, padx=(0, 10))
        
        # Export buttons
        export_frame = ttk.Frame(control_frame)
        export_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(export_frame, text="💾 Save .dat", command=self.save_dat).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="💾 Save .bin", command=self.save_bin).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Canvas frame
        canvas_frame = ttk.LabelFrame(main_frame, text="LED Matrix", padding=10)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value=f"Ready - {self.leds} LEDs")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def create_canvas(self):
        """Create the LED matrix canvas"""
        # Canvas frame
        canvas_container = ttk.Frame(self.dialog.winfo_children()[0].winfo_children()[-2])
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas
        self.canvas = tk.Canvas(canvas_container, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        
        # Draw grid
        self.draw_grid()
        
    def draw_grid(self):
        """Draw the LED grid"""
        self.canvas.delete("all")
        
        # Calculate cell size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized, schedule redraw
            self.dialog.after(100, self.draw_grid)
            return
        
        cell_width = canvas_width / self.matrix_size[0]
        cell_height = canvas_height / self.matrix_size[1]
        
        # Draw grid lines
        for i in range(self.matrix_size[0] + 1):
            x = i * cell_width
            self.canvas.create_line(x, 0, x, canvas_height, fill="gray", width=1)
            
        for i in range(self.matrix_size[1] + 1):
            y = i * cell_height
            self.canvas.create_line(0, y, canvas_width, y, fill="gray", width=1)
        
        # Draw LEDs
        for y in range(self.matrix_size[1]):
            for x in range(self.matrix_size[0]):
                led_index = y * self.matrix_size[0] + x
                if led_index < len(self.pattern_data):
                    r, g, b = self.pattern_data[led_index]
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    x1 = x * cell_width + 2
                    y1 = y * cell_height + 2
                    x2 = (x + 1) * cell_width - 2
                    y2 = (y + 1) * cell_height - 2
                    
                    self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="white", width=1)
        
        # Update status
        self.status_var.set(f"Matrix: {self.matrix_size[0]}x{self.matrix_size[1]} - {self.leds} LEDs")
        
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        self.update_led_at_position(event.x, event.y)
        
    def on_canvas_drag(self, event):
        """Handle canvas drag events"""
        self.update_led_at_position(event.x, event.y)
        
    def update_led_at_position(self, x, y):
        """Update LED at given canvas position"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        cell_width = canvas_width / self.matrix_size[0]
        cell_height = canvas_height / self.matrix_size[1]
        
        grid_x = int(x / cell_width)
        grid_y = int(y / cell_height)
        
        if 0 <= grid_x < self.matrix_size[0] and 0 <= grid_y < self.matrix_size[1]:
            led_index = grid_y * self.matrix_size[0] + grid_x
            if led_index < len(self.pattern_data):
                # Parse current color
                color = self.color_var.get()
                if color.startswith("#") and len(color) == 7:
                    try:
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)
                        self.pattern_data[led_index] = [r, g, b]
                        self.draw_grid()
                    except ValueError:
                        pass
                        
    def pick_color(self):
        """Open color picker dialog"""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(title="Pick LED Color")[1]
            if color:
                self.color_var.set(color)
                self.color_button.config(bg=color)
        except ImportError:
            # Fallback to simple color selection
            colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#000000"]
            current = colors.index(self.color_var.get()) if self.color_var.get() in colors else 0
            next_color = colors[(current + 1) % len(colors)]
            self.color_var.set(next_color)
            self.color_button.config(bg=next_color)
            
    def clear_pattern(self):
        """Clear all LEDs to black"""
        self.pattern_data = [[0, 0, 0] for _ in range(self.leds)]
        self.draw_grid()
        
    def random_pattern(self):
        """Generate random pattern"""
        import random
        self.pattern_data = [[random.randint(0, 255) for _ in range(3)] for _ in range(self.leds)]
        self.draw_grid()
        
    def import_image(self):
        """Import image and convert to LED pattern"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Import Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
            )
            if filename:
                # Load and resize image
                img = Image.open(filename)
                img = img.resize(self.matrix_size, Image.Resampling.LANCZOS)
                
                # Convert to RGB pattern
                for y in range(self.matrix_size[1]):
                    for x in range(self.matrix_size[0]):
                        led_index = y * self.matrix_size[0] + x
                        if led_index < len(self.pattern_data):
                            pixel = img.getpixel((x, y))
                            if len(pixel) >= 3:
                                self.pattern_data[led_index] = list(pixel[:3])
                            else:
                                self.pattern_data[led_index] = [pixel[0], pixel[0], pixel[0]]
                
                self.draw_grid()
                self.status_var.set(f"Imported image: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import image:\n{str(e)}")
            
    def save_dat(self):
        """Save pattern as .dat file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Save LED Pattern",
                defaultextension=".dat",
                filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
            )
            if filename:
                # Convert pattern to bytes
                data = bytearray()
                for led in self.pattern_data:
                    data.extend(led)
                
                with open(filename, 'wb') as f:
                    f.write(data)
                
                self.status_var.set(f"Saved: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Pattern saved as {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save pattern:\n{str(e)}")
            
    def save_bin(self):
        """Save pattern as .bin file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="Save LED Pattern",
                defaultextension=".bin",
                filetypes=[("BIN files", "*.bin"), ("All files", "*.*")]
            )
            if filename:
                # Convert pattern to bytes
                data = bytearray()
                for led in self.pattern_data:
                    data.extend(led)
                
                with open(filename, 'wb') as f:
                    f.write(data)
                
                self.status_var.set(f"Saved: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Pattern saved as {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save pattern:\n{str(e)}")
            
    def on_size_change(self, event=None):
        """Handle matrix size change"""
        try:
            size_str = self.size_var.get()
            width, height = map(int, size_str.split('x'))
            self.matrix_size = (width, height)
            self.leds = width * height
            self.pattern_data = [[0, 0, 0] for _ in range(self.leds)]
            self.draw_grid()
        except ValueError:
            pass
 
def main():
    root = tk.Tk()
    app = JTechPixelUploader(root)
    root.mainloop()

if __name__ == "__main__":
    main()
