#!/usr/bin/env python3
"""
Build script for creating draggg executables using PyInstaller.
Supports Linux, macOS, and Windows.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Install PyInstaller."""
    print("Installing PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0"], check=True)
    print("PyInstaller installed successfully!")


def build_linux():
    """Build Linux executables."""
    print("\n" + "=" * 60)
    print("Building Linux executables...")
    print("=" * 60)
    
    spec_files = [
        "pyinstaller/draggg.spec",
        "pyinstaller/draggg_gui.spec",
    ]
    
    for spec_file in spec_files:
        if not Path(spec_file).exists():
            print(f"Error: Spec file not found: {spec_file}")
            continue
        
        print(f"\nBuilding {spec_file}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "PyInstaller", spec_file, "--clean"],
                check=True
            )
            print(f"✓ Successfully built {spec_file}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build {spec_file}: {e}")
            return False
    
    print("\n✓ Linux executables built successfully!")
    print("  Output directory: dist/")
    return True


def build_mac():
    """Build macOS executables."""
    print("\n" + "=" * 60)
    print("Building macOS executables...")
    print("=" * 60)
    
    if platform.system() != "Darwin":
        print("Warning: macOS builds should be done on a Mac!")
        print("Continuing anyway...")
    
    spec_files = [
        "pyinstaller/draggg_mac.spec",
        "pyinstaller/draggg_gui_mac.spec",
    ]
    
    for spec_file in spec_files:
        if not Path(spec_file).exists():
            print(f"Error: Spec file not found: {spec_file}")
            continue
        
        print(f"\nBuilding {spec_file}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "PyInstaller", spec_file, "--clean"],
                check=True
            )
            print(f"✓ Successfully built {spec_file}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build {spec_file}: {e}")
            return False
    
    print("\n✓ macOS executables built successfully!")
    print("  Output directory: dist/")
    return True


def build_windows():
    """Build Windows executables."""
    print("\n" + "=" * 60)
    print("Building Windows executables...")
    print("=" * 60)
    
    if platform.system() != "Windows":
        print("Warning: Windows builds should be done on Windows!")
        print("Continuing anyway...")
    
    spec_files = [
        "pyinstaller/draggg_win.spec",
        "pyinstaller/draggg_gui_win.spec",
    ]
    
    for spec_file in spec_files:
        if not Path(spec_file).exists():
            print(f"Error: Spec file not found: {spec_file}")
            continue
        
        print(f"\nBuilding {spec_file}...")
        try:
            subprocess.run(
                [sys.executable, "-m", "PyInstaller", spec_file, "--clean"],
                check=True
            )
            print(f"✓ Successfully built {spec_file}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build {spec_file}: {e}")
            return False
    
    print("\n✓ Windows executables built successfully!")
    print("  Output directory: dist/")
    return True


def main():
    """Main build function."""
    print("draggg Executable Builder")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        try:
            install_pyinstaller()
        except Exception as e:
            print(f"Failed to install PyInstaller: {e}")
            print("Please install manually: pip install pyinstaller")
            return 1
    
    # Determine platform
    system = platform.system()
    
    print(f"\nDetected platform: {system}")
    print("\nAvailable build options:")
    print("  1. Linux")
    print("  2. macOS")
    print("  3. Windows")
    print("  4. All platforms")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1].lower()
    else:
        choice = input("\nSelect platform to build (1-4): ").strip()
    
    success = True
    
    if choice == "1" or choice == "linux":
        success = build_linux()
    elif choice == "2" or choice == "mac" or choice == "macos":
        success = build_mac()
    elif choice == "3" or choice == "windows" or choice == "win":
        success = build_windows()
    elif choice == "4" or choice == "all":
        success = build_linux() and build_mac() and build_windows()
    else:
        print("Invalid choice. Building for current platform...")
        if system == "Linux":
            success = build_linux()
        elif system == "Darwin":
            success = build_mac()
        elif system == "Windows":
            success = build_windows()
        else:
            print(f"Unknown platform: {system}")
            return 1
    
    if success:
        print("\n" + "=" * 60)
        print("Build completed successfully!")
        print("=" * 60)
        print("\nExecutables are in the 'dist' directory.")
        return 0
    else:
        print("\n" + "=" * 60)
        print("Build completed with errors.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
