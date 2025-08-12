#!/usr/bin/env python3
"""
Enhanced Progress Tracking System
Provides detailed upload progress with time estimates and speed calculations
"""

import tkinter as tk
from tkinter import ttk
import time
import threading

class EnhancedProgressTracker:
    """Enhanced progress tracking with time estimates and speed calculations"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.upload_start_time = None
        self.last_progress_update = None
        self.progress_history = []
        self.upload_speed = 0
        self.estimated_total_time = 0
        
        self.setup_progress_ui()
    
    def setup_progress_ui(self):
        """Setup the enhanced progress UI"""
        # Progress frame
        self.progress_frame = ttk.LabelFrame(self.parent_frame, text="📊 Enhanced Progress Tracking", padding="10")
        self.progress_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Main progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, maximum=100, length=600, mode='determinate')
        self.progress_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Progress details frame
        details_frame = ttk.Frame(self.progress_frame)
        details_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Progress percentage
        self.progress_label = ttk.Label(details_frame, text="Ready", font=("Arial", 10, "bold"))
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        # Time remaining
        self.time_remaining_label = ttk.Label(details_frame, text="", font=("Arial", 9))
        self.time_remaining_label.grid(row=0, column=1, padx=(20, 0))
        
        # Upload speed
        self.upload_speed_label = ttk.Label(details_frame, text="", font=("Arial", 9))
        self.upload_speed_label.grid(row=0, column=2, padx=(20, 0))
        
        # Status message
        self.status_message_label = ttk.Label(details_frame, text="", font=("Arial", 9))
        self.status_message_label.grid(row=0, column=3, padx=(20, 0))
        
        # Progress details frame
        details_frame2 = ttk.Frame(self.progress_frame)
        details_frame2.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Elapsed time
        self.elapsed_time_label = ttk.Label(details_frame2, text="", font=("Arial", 9))
        self.elapsed_time_label.grid(row=0, column=0, sticky=tk.W)
        
        # Data transferred
        self.data_transferred_label = ttk.Label(details_frame2, text="", font=("Arial", 9))
        self.data_transferred_label.grid(row=0, column=1, padx=(20, 0))
        
        # ETA
        self.eta_label = ttk.Label(details_frame2, text="", font=("Arial", 9))
        self.eta_label.grid(row=0, column=2, padx=(20, 0))
        
        # Progress graph (simple text-based)
        self.progress_graph_label = ttk.Label(details_frame2, text="", font=("Consolas", 8))
        self.progress_graph_label.grid(row=0, column=3, padx=(20, 0))
        
        # Configure grid weights
        self.progress_frame.columnconfigure(0, weight=1)
    
    def start_upload(self, total_size_bytes=None):
        """Start a new upload session"""
        self.upload_start_time = time.time()
        self.last_progress_update = time.time()
        self.progress_history = []
        self.upload_speed = 0
        self.estimated_total_time = 0
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Starting upload...")
        self.time_remaining_label.config(text="")
        self.upload_speed_label.config(text="")
        self.status_message_label.config(text="Initializing...")
        self.elapsed_time_label.config(text="Elapsed: 0s")
        self.data_transferred_label.config(text="")
        self.eta_label.config(text="")
        self.progress_graph_label.config(text="")
        
        # Start progress update thread
        self.progress_update_thread = threading.Thread(target=self.progress_update_loop, daemon=True)
        self.progress_update_thread.start()
    
    def update_progress(self, progress_percent, status_message="", data_transferred_bytes=None):
        """Update progress with enhanced information"""
        current_time = time.time()
        
        # Update progress bar
        self.progress_bar['value'] = progress_percent
        self.progress_label.config(text=f"{progress_percent:.1f}%")
        self.status_message_label.config(text=status_message)
        
        # Record progress history
        self.progress_history.append({
            'time': current_time,
            'progress': progress_percent,
            'data_transferred': data_transferred_bytes
        })
        
        # Calculate upload speed
        if len(self.progress_history) >= 2 and data_transferred_bytes:
            last_record = self.progress_history[-2]
            time_diff = current_time - last_record['time']
            data_diff = data_transferred_bytes - last_record.get('data_transferred', 0)
            
            if time_diff > 0:
                self.upload_speed = data_diff / time_diff  # bytes per second
        
        # Update data transferred
        if data_transferred_bytes:
            self.data_transferred_label.config(text=f"Data: {self.format_bytes(data_transferred_bytes)}")
        
        # Calculate time estimates
        if self.upload_start_time and progress_percent > 0:
            elapsed = current_time - self.upload_start_time
            self.elapsed_time_label.config(text=f"Elapsed: {self.format_time(elapsed)}")
            
            if progress_percent < 100:
                estimated_total = elapsed * 100 / progress_percent
                remaining = estimated_total - elapsed
                self.time_remaining_label.config(text=f"⏱️ {self.format_time(remaining)} remaining")
                
                # ETA
                eta_time = time.time() + remaining
                eta_str = time.strftime("%H:%M:%S", time.localtime(eta_time))
                self.eta_label.config(text=f"ETA: {eta_str}")
        
        # Update upload speed
        if self.upload_speed > 0:
            speed_str = f"📊 {self.format_bytes(self.upload_speed)}/s"
            self.upload_speed_label.config(text=speed_str)
        
        # Update progress graph
        self.update_progress_graph(progress_percent)
        
        # Force UI update
        self.parent_frame.update_idletasks()
    
    def update_progress_graph(self, progress_percent):
        """Update simple text-based progress graph"""
        bar_length = 20
        filled_length = int(bar_length * progress_percent / 100)
        
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        self.progress_graph_label.config(text=f"[{bar}] {progress_percent:.0f}%")
    
    def progress_update_loop(self):
        """Background loop for updating progress information"""
        while self.upload_start_time and time.time() - self.upload_start_time < 3600:  # Max 1 hour
            try:
                current_time = time.time()
                
                # Update elapsed time every second
                if self.upload_start_time:
                    elapsed = current_time - self.upload_start_time
                    self.parent_frame.after(0, lambda: self.elapsed_time_label.config(
                        text=f"Elapsed: {self.format_time(elapsed)}"))
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Progress update error: {e}")
                break
    
    def complete_upload(self, success=True):
        """Mark upload as complete"""
        if self.upload_start_time:
            total_time = time.time() - self.upload_start_time
            
            if success:
                self.progress_label.config(text="✅ Upload Complete!")
                self.status_message_label.config(text=f"Completed in {self.format_time(total_time)}")
                self.progress_bar['value'] = 100
            else:
                self.progress_label.config(text="❌ Upload Failed")
                self.status_message_label.config(text=f"Failed after {self.format_time(total_time)}")
            
            # Final statistics
            if self.upload_speed > 0:
                self.upload_speed_label.config(text=f"Final speed: {self.format_bytes(self.upload_speed)}/s")
            
            self.eta_label.config(text="")
            self.time_remaining_label.config(text="")
    
    def format_bytes(self, bytes_value):
        """Format bytes into human readable format"""
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.1f} KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_value / (1024 * 1024 * 1024):.1f} GB"
    
    def format_time(self, seconds):
        """Format seconds into human readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def get_upload_statistics(self):
        """Get comprehensive upload statistics"""
        if not self.upload_start_time:
            return None
        
        total_time = time.time() - self.upload_start_time
        
        stats = {
            'total_time': total_time,
            'formatted_time': self.format_time(total_time),
            'average_speed': self.upload_speed,
            'formatted_speed': self.format_bytes(self.upload_speed) + "/s" if self.upload_speed > 0 else "N/A",
            'progress_history': self.progress_history
        }
        
        return stats
    
    def reset(self):
        """Reset progress tracker"""
        self.upload_start_time = None
        self.last_progress_update = None
        self.progress_history = []
        self.upload_speed = 0
        self.estimated_total_time = 0
        
        # Reset UI
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready")
        self.time_remaining_label.config(text="")
        self.upload_speed_label.config(text="")
        self.status_message_label.config(text="")
        self.elapsed_time_label.config(text="")
        self.data_transferred_label.config(text="")
        self.eta_label.config(text="")
        self.progress_graph_label.config(text="")

# Example usage:
# progress_tracker = EnhancedProgressTracker(parent_frame)
# progress_tracker.start_upload(total_size_bytes=1024000)
# progress_tracker.update_progress(50, "Writing firmware...", 512000)
# progress_tracker.complete_upload(success=True)
