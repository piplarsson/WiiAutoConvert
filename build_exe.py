#!/usr/bin/env python3
"""
Build script for creating WiiAutoConvert executable.
Uses PyInstaller to create a standalone executable.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Build executable using PyInstaller."""
    print("Building WiiAutoConvert executable...")
    print("=" * 60)
    
    # Check if PyInstaller is installed, install if missing
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully!")
            # Try importing again
            import PyInstaller
        except Exception as e:
            print(f"ERROR: Failed to install PyInstaller: {e}")
            print("Please install manually with: pip install pyinstaller")
            sys.exit(1)
    
    # PyInstaller command (use python -m PyInstaller for better compatibility)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=WiiAutoConvert",
        "--onefile",
        "--windowed",  # No console window for GUI
        "--icon=NONE",  # Add icon file path here if you have one
        "--add-data=tools;tools",  # Include tools directory (Windows)
        "--hidden-import=customtkinter",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--collect-all=customtkinter",
        "--noconfirm",  # Overwrite output without asking
        "main.py"
    ]
    
    # Adjust for Linux/macOS
    if sys.platform != "win32":
        # Replace Windows path separator with Unix
        cmd = [arg.replace(";", ":") if "tools" in arg else arg for arg in cmd]
    
    print(f"Running: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 60)
        print("Build successful!")
        print(f"Executable location: dist/WiiAutoConvert.exe" if sys.platform == "win32" else "dist/WiiAutoConvert")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("Build failed!")
        print(f"Error: {e}")
        print("=" * 60)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: PyInstaller not found in PATH.")
        print("Make sure PyInstaller is installed: pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    main()

