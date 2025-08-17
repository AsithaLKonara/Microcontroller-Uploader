#!/usr/bin/env python3
"""
Test script for the dependency installer dialog
This script tests the dependency installer UI without running the full application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import sys
import os

class MockDependencyInstaller:
    """Mock class to test the dependency installer dialog"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dependency Installer Test")
        self.root.geometry("600x500")
        self.root.configure(bg='#f8fafc')
        
        # Mock colors
        self.colors = {
            'background': '#f8fafc',
            'card_bg': '#ffffff',
            'primary': '#3b82f6',
            'text_primary': '#1e293b',
            'text_secondary': '#475569',
            'success': '#22c55e',
            'warning': '#facc15',
            'error': '#ef4444'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the test UI"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🧪 Dependency Installer Test", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Test buttons
        test_frame = ttk.Frame(main_frame)
        test_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(test_frame, text="Test Missing pyserial", 
                  command=lambda: self.test_missing_pyserial()).pack(side='left', padx=(0, 10))
        
        ttk.Button(test_frame, text="Test Missing esptool", 
                  command=lambda: self.test_missing_esptool()).pack(side='left', padx=(0, 10))
        
        ttk.Button(test_frame, text="Test Missing Both", 
                  command=lambda: self.test_missing_both()).pack(side='left')
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready for testing", 
                                     font=('Segoe UI', 10))
        self.status_label.pack(pady=(0, 20))
        
        # Instructions
        instructions = """
        This test simulates the dependency installer dialog.
        
        Click the test buttons to see how the installer would behave
        with different missing dependencies.
        
        The installer will show:
        • List of missing packages
        • Install button with progress
        • Manual installation instructions
        • Success/error handling
        """
        
        info_label = ttk.Label(main_frame, text=instructions, 
                              font=('Segoe UI', 9), justify='left')
        info_label.pack(fill='x', pady=(0, 20))
        
    def test_missing_pyserial(self):
        """Test installer with missing pyserial"""
        self.status_label.config(text="Testing missing pyserial...")
        self.show_dependency_installer(['pyserial'])
        
    def test_missing_esptool(self):
        """Test installer with missing esptool"""
        self.status_label.config(text="Testing missing esptool...")
        self.show_dependency_installer(['esptool'])
        
    def test_missing_both(self):
        """Test installer with missing both packages"""
        self.status_label.config(text="Testing missing both packages...")
        self.show_dependency_installer(['pyserial', 'esptool'])
        
    def show_dependency_installer(self, missing_packages):
        """Show dependency installation dialog (same as in main.py)"""
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
        main_frame = ttk.Frame(self.dep_window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🔧 Missing Dependencies Detected", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(20, 10))
        
        # Description
        desc_label = ttk.Label(main_frame, 
                               text="The following required packages are not installed:",
                               font=('Segoe UI', 12))
        desc_label.pack(pady=(0, 20))
        
        # Missing packages list
        for package in missing_packages:
            pkg_label = ttk.Label(main_frame, 
                                  text=f"• {package}", 
                                  font=('Segoe UI', 12, 'bold'))
            pkg_label.pack(anchor='w', pady=2)
        
        # Installation info
        info_label = ttk.Label(main_frame, 
                               text="Click 'Install Dependencies' to automatically install them via pip",
                               font=('Segoe UI', 12))
        info_label.pack(pady=(20, 20))
        
        # Progress bar
        self.install_progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.install_progress.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status label
        self.install_status = ttk.Label(main_frame, 
                                       text="Ready to install", 
                                       font=('Segoe UI', 10))
        self.install_status.pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Install button
        install_btn = ttk.Button(buttons_frame, 
                                text="Install Dependencies", 
                                command=lambda: self.install_dependencies(missing_packages))
        install_btn.pack(side='left', padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, 
                               text="Cancel", 
                               command=self.dep_window.destroy)
        cancel_btn.pack(side='left')
        
        # Manual install info
        manual_info = ttk.Label(main_frame, 
                               text="Or install manually: pip install " + " ".join(missing_packages),
                               font=('Segoe UI', 9))
        manual_info.pack(pady=(20, 0))
        
    def install_dependencies(self, packages):
        """Install missing dependencies using pip (simulated)"""
        def install_thread():
            try:
                self.install_status.config(text="Installing dependencies...")
                self.install_progress.start()
                
                for package in packages:
                    self.install_status.config(text=f"Installing {package}...")
                    
                    # Simulate installation delay
                    import time
                    time.sleep(2)
                    
                    # Simulate successful installation
                    print(f"✅ Successfully installed {package} (simulated)")
                
                self.install_status.config(text="Installation completed successfully!")
                self.install_progress.stop()
                
                # Show success message
                messagebox.showinfo("Success", 
                                  "All dependencies have been installed successfully!\n"
                                  "(This was a simulation)")
                
                # Close the installer window
                self.dep_window.destroy()
                
            except Exception as e:
                self.install_progress.stop()
                self.install_status.config(text=f"Installation failed: {str(e)}")
                messagebox.showerror("Installation Error", 
                                   f"Failed to install dependencies:\n{str(e)}")
                print(f"❌ Dependency installation failed: {e}")
        
        # Run installation in separate thread
        threading.Thread(target=install_thread, daemon=True).start()
    
    def run(self):
        """Run the test application"""
        self.root.mainloop()

def main():
    """Main test function"""
    print("🧪 Starting Dependency Installer Test")
    print("This will open a test window to verify the dependency installer UI")
    
    app = MockDependencyInstaller()
    app.run()

if __name__ == "__main__":
    main()
