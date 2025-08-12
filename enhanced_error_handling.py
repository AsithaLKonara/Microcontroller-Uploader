#!/usr/bin/env python3
"""
Enhanced Error Handling System
Provides intelligent error detection, recovery suggestions, and automatic retry logic
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import json
import os
from datetime import datetime

class EnhancedErrorHandler:
    """Enhanced error handling with intelligent recovery and suggestions"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.error_history = []
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        self.error_patterns = self.load_error_patterns()
        
        # Setup error logging
        self.error_log_file = "error_log.json"
        self.load_error_history()
    
    def load_error_patterns(self):
        """Load predefined error patterns and solutions"""
        return {
            "connection_errors": {
                "patterns": [
                    "Access is denied",
                    "File not found",
                    "Device not ready",
                    "Connection refused",
                    "Timeout",
                    "Port already in use"
                ],
                "solutions": [
                    "Check if another application is using the port",
                    "Verify the device is connected and powered on",
                    "Try a different COM port",
                    "Restart the device",
                    "Check USB cable connection"
                ]
            },
            "upload_errors": {
                "patterns": [
                    "Upload failed",
                    "Verification failed",
                    "Flash error",
                    "Memory error",
                    "CRC error"
                ],
                "solutions": [
                    "Put device in flash mode (hold FLASH button while powering on)",
                    "Check firmware file compatibility",
                    "Verify device type selection",
                    "Try lower baud rate",
                    "Check power supply stability"
                ]
            },
            "device_errors": {
                "patterns": [
                    "Device not responding",
                    "Invalid device",
                    "Unsupported device",
                    "Device timeout"
                ],
                "solutions": [
                    "Verify device type selection",
                    "Check device connections",
                    "Try different baud rate",
                    "Reset device to factory settings",
                    "Update device drivers"
                ]
            },
            "firmware_errors": {
                "patterns": [
                    "Invalid firmware",
                    "File corrupted",
                    "Wrong firmware type",
                    "Size mismatch"
                ],
                "solutions": [
                    "Verify firmware file integrity",
                    "Check file format compatibility",
                    "Download firmware again",
                    "Verify checksum",
                    "Check file size requirements"
                ]
            }
        }
    
    def load_error_history(self):
        """Load error history from file"""
        try:
            if os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'r') as f:
                    self.error_history = json.load(f)
            else:
                self.error_history = []
        except Exception as e:
            print(f"Error loading error history: {e}")
            self.error_history = []
    
    def save_error_history(self):
        """Save error history to file"""
        try:
            with open(self.error_log_file, 'w') as f:
                json.dump(self.error_history, f, indent=2)
        except Exception as e:
            print(f"Error saving error history: {e}")
    
    def handle_error(self, error, context=None, error_type="GENERAL"):
        """Main error handling method"""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "error_type": error_type,
            "context": context or {},
            "traceback": self.get_traceback(),
            "recovery_attempts": 0
        }
        
        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > 100:  # Keep only last 100 errors
            self.error_history = self.error_history[-100:]
        
        # Save to file
        self.save_error_history()
        
        # Analyze error and get suggestions
        suggestions = self.analyze_error(error_info)
        
        # Log error
        self.log_error(error_info, suggestions)
        
        # Show error dialog
        self.show_error_dialog(error_info, suggestions)
        
        # Attempt automatic recovery if possible
        if self.should_attempt_recovery(error_info):
            self.attempt_automatic_recovery(error_info)
        
        return error_info
    
    def analyze_error(self, error_info):
        """Analyze error and provide intelligent suggestions"""
        error_text = error_info["error"].lower()
        suggestions = []
        
        # Check against known patterns
        for category, patterns in self.error_patterns.items():
            for pattern in patterns["patterns"]:
                if pattern.lower() in error_text:
                    suggestions.extend(patterns["solutions"])
                    break
        
        # Add general suggestions if none found
        if not suggestions:
            suggestions = [
                "Check all connections",
                "Verify device power",
                "Restart the application",
                "Check system requirements",
                "Update device drivers"
            ]
        
        # Add context-specific suggestions
        context = error_info.get("context", {})
        if "device_type" in context:
            device_specific = self.get_device_specific_suggestions(context["device_type"])
            suggestions.extend(device_specific)
        
        # Remove duplicates and limit to top 5
        unique_suggestions = list(dict.fromkeys(suggestions))[:5]
        
        return unique_suggestions
    
    def get_device_specific_suggestions(self, device_type):
        """Get device-specific error suggestions"""
        device_suggestions = {
            "ESP8266": [
                "Hold FLASH button while powering on",
                "Check GPIO0 connection for flash mode",
                "Verify 3.3V power supply",
                "Check CH_PD/EN pin connection"
            ],
            "ESP32": [
                "Hold BOOT button while powering on",
                "Check GPIO0 and GPIO2 connections",
                "Verify 3.3V power supply",
                "Check EN pin connection"
            ],
            "AVR": [
                "Check ISP programmer connection",
                "Verify target voltage (usually 5V)",
                "Check clock crystal connections",
                "Verify fuse settings"
            ]
        }
        
        return device_suggestions.get(device_type, [])
    
    def get_traceback(self):
        """Get current traceback information"""
        import traceback
        try:
            return traceback.format_exc()
        except:
            return "Traceback not available"
    
    def log_error(self, error_info, suggestions):
        """Log error with suggestions"""
        timestamp = error_info["timestamp"]
        error_msg = error_info["error"]
        error_type = error_info["error_type"]
        
        log_message = f"[{timestamp}] {error_type} ERROR: {error_msg}"
        print(log_message)
        
        # Log to main application if possible
        if hasattr(self.main_app, 'log_message'):
            self.main_app.log_message(f"❌ {error_type} Error: {error_msg}", "ERROR")
            for suggestion in suggestions:
                self.main_app.log_message(f"💡 Suggestion: {suggestion}", "INFO")
    
    def show_error_dialog(self, error_info, suggestions):
        """Show enhanced error dialog with suggestions"""
        error_dialog = tk.Toplevel(self.main_app.root)
        error_dialog.title("Enhanced Error Handler")
        error_dialog.geometry("600x500")
        error_dialog.resizable(True, True)
        
        # Make dialog modal
        error_dialog.transient(self.main_app.root)
        error_dialog.grab_set()
        
        # Main container
        main_frame = ttk.Frame(error_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Error icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        error_icon = ttk.Label(title_frame, text="❌", font=("Arial", 24))
        error_icon.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="Error Detected", 
                               font=("Arial", 16, "bold"), foreground="red")
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Error details
        details_frame = ttk.LabelFrame(main_frame, text="Error Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        error_type_label = ttk.Label(details_frame, text=f"Type: {error_info['error_type']}", 
                                    font=("Arial", 10, "bold"))
        error_type_label.pack(anchor=tk.W)
        
        error_msg_label = ttk.Label(details_frame, text=f"Message: {error_info['error']}", 
                                   font=("Arial", 10))
        error_msg_label.pack(anchor=tk.W, pady=(5, 0))
        
        timestamp_label = ttk.Label(details_frame, text=f"Time: {error_info['timestamp']}", 
                                   font=("Arial", 9), foreground="gray")
        timestamp_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Suggestions frame
        suggestions_frame = ttk.LabelFrame(main_frame, text="💡 Recovery Suggestions", padding="10")
        suggestions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Suggestions list
        suggestions_text = tk.Text(suggestions_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
        suggestions_scrollbar = ttk.Scrollbar(suggestions_frame, orient=tk.VERTICAL, 
                                            command=suggestions_text.yview)
        suggestions_text.configure(yscrollcommand=suggestions_scrollbar.set)
        
        suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suggestions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate suggestions
        for i, suggestion in enumerate(suggestions, 1):
            suggestions_text.insert(tk.END, f"{i}. {suggestion}\n\n")
        
        suggestions_text.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Auto-recovery button
        auto_recovery_btn = ttk.Button(button_frame, text="🔄 Try Auto-Recovery", 
                                     command=lambda: self.attempt_automatic_recovery(error_info))
        auto_recovery_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Manual recovery button
        manual_recovery_btn = ttk.Button(button_frame, text="🔧 Manual Recovery Guide", 
                                       command=lambda: self.show_manual_recovery_guide(error_info))
        manual_recovery_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Report button
        report_btn = ttk.Button(button_frame, text="📊 Report Issue", 
                               command=lambda: self.report_issue(error_info))
        report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(button_frame, text="Close", 
                              command=error_dialog.destroy)
        close_btn.pack(side=tk.RIGHT)
        
        # Center dialog on screen
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() // 2) - (error_dialog.winfo_width() // 2)
        y = (error_dialog.winfo_screenheight() // 2) - (error_dialog.winfo_width() // 2)
        error_dialog.geometry(f"+{x}+{y}")
    
    def should_attempt_recovery(self, error_info):
        """Determine if automatic recovery should be attempted"""
        error_type = error_info["error_type"]
        
        # Don't attempt recovery for certain error types
        non_recoverable = ["CRITICAL", "SYSTEM", "PERMISSION"]
        if error_type in non_recoverable:
            return False
        
        # Check recovery attempt limit
        error_key = f"{error_type}_{error_info['error']}"
        if error_key in self.recovery_attempts:
            if self.recovery_attempts[error_key] >= self.max_recovery_attempts:
                return False
        
        return True
    
    def attempt_automatic_recovery(self, error_info):
        """Attempt automatic error recovery"""
        error_key = f"{error_info['error_type']}_{error_info['error']}"
        
        # Increment recovery attempts
        if error_key in self.recovery_attempts:
            self.recovery_attempts[error_key] += 1
        else:
            self.recovery_attempts[error_key] = 1
        
        # Log recovery attempt
        print(f"Attempting automatic recovery for: {error_info['error']}")
        
        # Implement recovery logic based on error type
        recovery_success = False
        
        try:
            if "connection" in error_info["error_type"].lower():
                recovery_success = self.recover_connection_error(error_info)
            elif "upload" in error_info["error_type"].lower():
                recovery_success = self.recover_upload_error(error_info)
            elif "device" in error_info["error_type"].lower():
                recovery_success = self.recover_device_error(error_info)
            else:
                recovery_success = self.recover_general_error(error_info)
        
        except Exception as e:
            print(f"Recovery attempt failed: {e}")
            recovery_success = False
        
        # Show recovery result
        if recovery_success:
            messagebox.showinfo("Recovery Success", "Automatic recovery was successful!")
        else:
            messagebox.showwarning("Recovery Failed", 
                                 "Automatic recovery failed. Please try manual recovery steps.")
    
    def recover_connection_error(self, error_info):
        """Recover from connection errors"""
        try:
            # Try to refresh available ports
            if hasattr(self.main_app, 'detect_available_ports'):
                self.main_app.detect_available_ports()
            
            # Try to test connection
            context = error_info.get("context", {})
            if "port" in context and "baud" in context:
                if hasattr(self.main_app, 'test_connection'):
                    return self.main_app.test_connection()
            
            return False
        except:
            return False
    
    def recover_upload_error(self, error_info):
        """Recover from upload errors"""
        try:
            # Try to reset device state
            context = error_info.get("context", {})
            if "port" in context:
                # Send reset command
                import serial
                ser = serial.Serial(context["port"], 115200, timeout=2)
                ser.write(b'AT+RST\r\n')
                ser.close()
                time.sleep(2)
                return True
            return False
        except:
            return False
    
    def recover_device_error(self, error_info):
        """Recover from device errors"""
        try:
            # Try to re-detect device
            if hasattr(self.main_app, 'auto_detect_devices'):
                self.main_app.auto_detect_devices()
                return True
            return False
        except:
            return False
    
    def recover_general_error(self, error_info):
        """Recover from general errors"""
        try:
            # Wait and retry
            time.sleep(2)
            return True
        except:
            return False
    
    def show_manual_recovery_guide(self, error_info):
        """Show manual recovery guide"""
        guide_window = tk.Toplevel(self.main_app.root)
        guide_window.title("Manual Recovery Guide")
        guide_window.geometry("700x600")
        
        # Create guide content based on error type
        guide_content = self.generate_recovery_guide(error_info)
        
        # Display guide
        text_widget = tk.Text(guide_window, wrap=tk.WORD, font=("Arial", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget.insert(tk.END, guide_content)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(guide_window, text="Close", 
                  command=guide_window.destroy).pack(pady=10)
    
    def generate_recovery_guide(self, error_info):
        """Generate recovery guide content"""
        error_type = error_info["error_type"]
        guide = f"Manual Recovery Guide for {error_type} Error\n"
        guide += "=" * 50 + "\n\n"
        
        if "connection" in error_type.lower():
            guide += self.get_connection_recovery_guide()
        elif "upload" in error_type.lower():
            guide += self.get_upload_recovery_guide()
        elif "device" in error_type.lower():
            guide += self.get_device_recovery_guide()
        else:
            guide += self.get_general_recovery_guide()
        
        return guide
    
    def get_connection_recovery_guide(self):
        """Get connection recovery guide"""
        return """Connection Error Recovery Steps:

1. Check Physical Connections:
   • Verify USB cable is properly connected
   • Try a different USB port
   • Check if cable is damaged

2. Device Power:
   • Ensure device is powered on
   • Check power LED indicators
   • Try different power source if applicable

3. Port Availability:
   • Close other applications using the port
   • Restart the device
   • Check Device Manager for port status

4. Driver Issues:
   • Update USB-to-Serial drivers
   • Reinstall device drivers
   • Check Windows Update for driver updates

5. System Restart:
   • Restart the application
   • Restart the computer if needed
   • Try on different computer if available"""
    
    def get_upload_recovery_guide(self):
        """Get upload recovery guide"""
        return """Upload Error Recovery Steps:

1. Device Mode:
   • Put device in flash/programming mode
   • For ESP8266: Hold FLASH button while powering on
   • For ESP32: Hold BOOT button while powering on

2. Firmware File:
   • Verify firmware file is not corrupted
   • Check file compatibility with device
   • Try different firmware version

3. Connection Settings:
   • Try lower baud rate (115200, 57600)
   • Check COM port selection
   • Verify device type selection

4. Power Supply:
   • Ensure stable power supply
   • Use external power if available
   • Check voltage requirements

5. Hardware Reset:
   • Disconnect and reconnect device
   • Try different USB cable
   • Check for loose connections"""
    
    def get_device_recovery_guide(self):
        """Get device recovery guide"""
        return """Device Error Recovery Steps:

1. Device Identification:
   • Verify correct device type selection
   • Check device specifications
   • Confirm device compatibility

2. Hardware Reset:
   • Power cycle the device
   • Press reset button if available
   • Check for hardware damage

3. Firmware Reset:
   • Reset to factory settings
   • Clear device memory
   • Reinstall default firmware

4. Connection Verification:
   • Check all pin connections
   • Verify wiring diagram
   • Test with known good device

5. Environment Check:
   • Check temperature conditions
   • Verify power requirements
   • Ensure proper grounding"""
    
    def get_general_recovery_guide(self):
        """Get general recovery guide"""
        return """General Error Recovery Steps:

1. Basic Troubleshooting:
   • Restart the application
   • Check system resources
   • Verify file permissions

2. System Check:
   • Update operating system
   • Check for system errors
   • Verify Python installation

3. Application Reset:
   • Clear application cache
   • Reset configuration
   • Reinstall application

4. Log Analysis:
   • Check error logs
   • Review system logs
   • Look for pattern in errors

5. Support:
   • Check documentation
   • Search for similar issues
   • Contact technical support"""
    
    def report_issue(self, error_info):
        """Report issue for analysis"""
        report_window = tk.Toplevel(self.main_app.root)
        report_window.title("Report Issue")
        report_window.geometry("500x400")
        
        # Report form
        ttk.Label(report_window, text="Issue Report", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Error summary
        ttk.Label(report_window, text="Error Summary:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20)
        error_summary = tk.Text(report_window, height=4, wrap=tk.WORD)
        error_summary.pack(fill=tk.X, padx=20, pady=5)
        error_summary.insert(tk.END, f"Type: {error_info['error_type']}\nError: {error_info['error']}\nContext: {error_info.get('context', {})}")
        
        # User description
        ttk.Label(report_window, text="Additional Details:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(10, 0))
        user_description = tk.Text(report_window, height=6, wrap=tk.WORD)
        user_description.pack(fill=tk.X, padx=20, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(report_window)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text="Generate Report", 
                  command=lambda: self.generate_issue_report(error_info, user_description.get("1.0", tk.END))).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", 
                  command=report_window.destroy).pack(side=tk.RIGHT)
    
    def generate_issue_report(self, error_info, user_description):
        """Generate issue report file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"issue_report_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("ISSUE REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Timestamp: {error_info['timestamp']}\n")
                f.write(f"Error Type: {error_info['error_type']}\n")
                f.write(f"Error Message: {error_info['error']}\n")
                f.write(f"Context: {error_info.get('context', {})}\n")
                f.write(f"Traceback: {error_info.get('traceback', 'N/A')}\n\n")
                f.write("User Description:\n")
                f.write(user_description)
                f.write("\n\nSystem Information:\n")
                f.write(f"Python Version: {self.get_python_version()}\n")
                f.write(f"Platform: {self.get_platform_info()}\n")
            
            messagebox.showinfo("Report Generated", f"Issue report saved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def get_python_version(self):
        """Get Python version information"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def get_platform_info(self):
        """Get platform information"""
        import platform
        return f"{platform.system()} {platform.release()} {platform.architecture()[0]}"
    
    def get_error_statistics(self):
        """Get error statistics for analysis"""
        if not self.error_history:
            return {}
        
        stats = {
            "total_errors": len(self.error_history),
            "error_types": {},
            "recent_errors": len([e for e in self.error_history if 
                                (datetime.now() - datetime.fromisoformat(e["timestamp"])).days < 1]),
            "recovery_success_rate": 0
        }
        
        # Count error types
        for error in self.error_history:
            error_type = error["error_type"]
            stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
        
        # Calculate recovery success rate
        successful_recoveries = len([e for e in self.error_history if 
                                   e.get("recovery_attempts", 0) > 0])
        if successful_recoveries > 0:
            stats["recovery_success_rate"] = (successful_recoveries / len(self.error_history)) * 100
        
        return stats

# Example usage:
# error_handler = EnhancedErrorHandler(main_app)
# error_handler.handle_error("Connection failed", {"port": "COM3"}, "CONNECTION")
