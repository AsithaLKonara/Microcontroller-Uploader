#!/usr/bin/env python3
"""
Minimal test script to isolate the text widget creation issue
"""

import tkinter as tk
from tkinter import ttk

def test_text_widget():
    """Test basic text widget creation"""
    root = tk.Tk()
    root.title("Text Widget Test")
    root.geometry("400x300")
    
    # Test 1: Basic text widget
    try:
        text1 = tk.Text(root, wrap=tk.WORD, width=60, height=30)
        text1.pack(pady=10)
        print("✅ Basic text widget created successfully")
    except Exception as e:
        print(f"❌ Basic text widget failed: {e}")
    
    # Test 2: Text widget with explicit int conversion
    try:
        text2 = tk.Text(root, wrap=tk.WORD, width=int(60), height=int(30))
        text2.pack(pady=10)
        print("✅ Text widget with int() created successfully")
    except Exception as e:
        print(f"❌ Text widget with int() failed: {e}")
    
    # Test 3: Text widget with string parameters
    try:
        text3 = tk.Text(root, wrap=tk.WORD, width="60", height="30")
        text3.pack(pady=10)
        print("✅ Text widget with string parameters created successfully")
    except Exception as e:
        print(f"❌ Text widget with string parameters failed: {e}")
    
    root.mainloop()

if __name__ == "__main__":
    test_text_widget()
