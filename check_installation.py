#!/usr/bin/env python3
"""
Post-installation verification script for draggg.
Checks that entry points are accessible and PATH is configured correctly.
"""

import sys
import shutil
import subprocess
from pathlib import Path


def check_entry_points():
    """Check if draggg and draggg-gui commands are accessible."""
    print("Checking entry points...")
    
    draggg_found = shutil.which("draggg")
    draggg_gui_found = shutil.which("draggg-gui")
    
    if draggg_found:
        print(f"✓ draggg found at: {draggg_found}")
    else:
        print("✗ draggg not found in PATH")
    
    if draggg_gui_found:
        print(f"✓ draggg-gui found at: {draggg_gui_found}")
    else:
        print("✗ draggg-gui not found in PATH")
    
    return draggg_found and draggg_gui_found


def check_scripts_directory():
    """Check where pip installed scripts and if it's in PATH."""
    print("\nChecking scripts installation...")
    
    try:
        import site
        user_base = Path(site.getuserbase())
        scripts_dir = user_base / "bin"
        
        print(f"Scripts directory: {scripts_dir}")
        print(f"Directory exists: {scripts_dir.exists()}")
        
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob("draggg*"))
            if scripts:
                print(f"Found scripts: {[s.name for s in scripts]}")
            else:
                print("No draggg scripts found in scripts directory")
        
        # Check if in PATH
        import os
        path_dirs = os.environ.get("PATH", "").split(":")
        in_path = str(scripts_dir) in path_dirs
        
        print(f"In PATH: {in_path}")
        
        if not in_path:
            print(f"\n⚠️  WARNING: {scripts_dir} is not in your PATH")
            print(f"Add it to PATH by running:")
            print(f'  echo \'export PATH="$HOME/.local/bin:$PATH"\' >> ~/.bashrc')
            print(f"  source ~/.bashrc")
        
        return in_path, scripts_dir
    except Exception as e:
        print(f"Error checking scripts directory: {e}")
        return False, None


def check_desktop_file():
    """Check if desktop file exists and has correct icon."""
    print("\nChecking desktop file...")
    
    desktop_file = Path.home() / ".local" / "share" / "applications" / "draggg.desktop"
    
    if desktop_file.exists():
        print(f"✓ Desktop file exists: {desktop_file}")
        
        content = desktop_file.read_text()
        if "Icon=draggg" in content:
            print("✓ Icon reference is correct (Icon=draggg)")
        else:
            print("⚠️  Icon reference may be incorrect")
            print(f"   Content: {content[:200]}...")
        
        if "Exec=draggg-gui" in content:
            print("✓ Exec command is correct (Exec=draggg-gui)")
        elif "Exec=" in content:
            exec_line = [line for line in content.split('\n') if line.startswith('Exec=')][0]
            print(f"⚠️  Exec command: {exec_line}")
            print("   Should be: Exec=draggg-gui")
        else:
            print("⚠️  Exec command not found")
    else:
        print(f"✗ Desktop file not found: {desktop_file}")
        print("   (This is normal if installed system-wide)")
    
    return desktop_file.exists()


def check_icons():
    """Check if icons are installed correctly."""
    print("\nChecking icons...")
    
    icon_base = Path.home() / ".local" / "share" / "icons" / "hicolor"
    icon_sizes = ["256x256", "128x128", "64x64", "48x48"]
    
    icons_found = []
    for size in icon_sizes:
        icon_path = icon_base / size / "apps" / "draggg.png"
        if icon_path.exists():
            icons_found.append(size)
            print(f"✓ Icon found ({size}): {icon_path}")
        else:
            # Check for old icon name
            old_icon = icon_base / size / "apps" / "icon.png"
            if old_icon.exists():
                print(f"⚠️  Old icon name found ({size}): {old_icon}")
                print(f"   Should be renamed to: draggg.png")
    
    if not icons_found:
        print("✗ No icons found in user directory")
        print("   (Icons may be installed system-wide)")
    
    return len(icons_found) > 0


def main():
    """Run all checks."""
    print("draggg Installation Verification")
    print("=" * 50)
    
    entry_points_ok = check_entry_points()
    path_ok, scripts_dir = check_scripts_directory()
    desktop_ok = check_desktop_file()
    icons_ok = check_icons()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Entry points accessible: {'✓' if entry_points_ok else '✗'}")
    print(f"  Scripts directory in PATH: {'✓' if path_ok else '✗'}")
    print(f"  Desktop file: {'✓' if desktop_ok else '✗'}")
    print(f"  Icons installed: {'✓' if icons_ok else '✗'}")
    
    if not entry_points_ok and scripts_dir:
        print(f"\n⚠️  To fix entry points, add to PATH:")
        print(f'   export PATH="{scripts_dir}:$PATH"')
        print(f"\n   Or add permanently to ~/.bashrc:")
        print(f'   echo \'export PATH="$HOME/.local/bin:$PATH"\' >> ~/.bashrc')
    
    if entry_points_ok and desktop_ok:
        print("\n✓ Installation looks good!")
        return 0
    else:
        print("\n⚠️  Some issues detected. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
