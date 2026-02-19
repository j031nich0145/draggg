#!/usr/bin/env python3
"""
Wayland to X11 Conversion Script
Automatically modifies display manager configuration files to disable Wayland.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict


def detect_distribution() -> str:
    """Detect Linux distribution."""
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"').strip("'")
    except Exception:
        pass
    
    # Fallback detection
    if os.path.exists('/etc/debian_version'):
        return 'debian'
    elif os.path.exists('/etc/redhat-release'):
        return 'fedora'
    elif os.path.exists('/etc/arch-release'):
        return 'arch'
    
    return 'unknown'


def detect_display_manager() -> Optional[str]:
    """Detect active display manager."""
    # Check /etc/X11/default-display-manager (if exists)
    default_dm_path = Path('/etc/X11/default-display-manager')
    if default_dm_path.exists():
        try:
            content = default_dm_path.read_text().strip()
            if 'gdm' in content.lower():
                return 'gdm'
            elif 'lightdm' in content.lower():
                return 'lightdm'
            elif 'sddm' in content.lower():
                return 'sddm'
        except Exception:
            pass
    
    # Check systemd for active display manager service
    try:
        for dm in ['gdm', 'gdm3', 'lightdm', 'sddm']:
            result = subprocess.run(
                ['systemctl', 'is-active', f'{dm}.service'],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                # Normalize gdm3 to gdm
                return 'gdm' if dm == 'gdm3' else dm
    except Exception:
        pass
    
    # Check config file existence as fallback
    if Path('/etc/gdm3/custom.conf').exists() or Path('/etc/gdm/custom.conf').exists():
        return 'gdm'
    elif Path('/etc/lightdm/lightdm.conf').exists():
        return 'lightdm'
    elif Path('/etc/sddm.conf').exists():
        return 'sddm'
    
    return None


def get_gdm_config_path(distro: str) -> Optional[str]:
    """Get GDM configuration file path for distribution."""
    if distro in ('ubuntu', 'debian'):
        return '/etc/gdm3/custom.conf'
    elif distro in ('fedora', 'rhel', 'centos'):
        return '/etc/gdm/custom.conf'
    else:
        # Try common locations
        for path in ['/etc/gdm3/custom.conf', '/etc/gdm/custom.conf']:
            if os.path.exists(path):
                return path
    
    return None


def get_config_path(display_manager: str, distro: str) -> Optional[str]:
    """Get configuration file path for display manager and distribution."""
    if display_manager == 'gdm':
        return get_gdm_config_path(distro)
    elif display_manager == 'lightdm':
        return '/etc/lightdm/lightdm.conf'
    elif display_manager == 'sddm':
        return '/etc/sddm.conf'
    
    return None


def backup_config(config_path: str) -> Optional[str]:
    """Create backup of config file before modification."""
    config_file = Path(config_path)
    if not config_file.exists():
        return None
    
    backup_path = f"{config_path}.backup"
    backup_file = Path(backup_path)
    
    # If backup already exists, add timestamp
    if backup_file.exists():
        import time
        timestamp = int(time.time())
        backup_path = f"{config_path}.backup.{timestamp}"
        backup_file = Path(backup_path)
    
    try:
        shutil.copy2(config_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Warning: Could not create backup: {e}", file=sys.stderr)
        return None


def modify_gdm_config(config_path: str) -> Tuple[bool, str]:
    """Modify GDM config file to disable Wayland."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return False, f"Config file not found: {config_path}"
    
    try:
        # Read current config
        content = config_file.read_text()
        lines = content.split('\n')
        
        modified = False
        in_daemon_section = False
        wayland_found = False
        
        # Process lines
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track if we're in [daemon] section
            if stripped == '[daemon]':
                in_daemon_section = True
                continue
            
            # If we hit another section, we're out of [daemon]
            if stripped.startswith('[') and stripped.endswith(']') and stripped != '[daemon]':
                in_daemon_section = False
                continue
            
            # Look for WaylandEnable line in [daemon] section
            if in_daemon_section:
                if '#WaylandEnable=false' in stripped:
                    # Uncomment the line
                    lines[i] = line.replace('#WaylandEnable=false', 'WaylandEnable=false')
                    modified = True
                    wayland_found = True
                    break
                elif 'WaylandEnable=false' in stripped and not stripped.startswith('#'):
                    # Already set correctly
                    wayland_found = True
                    break
                elif 'WaylandEnable=true' in stripped:
                    # Change true to false
                    lines[i] = line.replace('WaylandEnable=true', 'WaylandEnable=false')
                    modified = True
                    wayland_found = True
                    break
        
        # If WaylandEnable not found, add it under [daemon] section
        if not wayland_found:
            # Find [daemon] section and add after it
            for i, line in enumerate(lines):
                if line.strip() == '[daemon]':
                    # Insert WaylandEnable=false after [daemon]
                    lines.insert(i + 1, 'WaylandEnable=false')
                    modified = True
                    break
        
        if modified:
            # Write modified config
            new_content = '\n'.join(lines)
            config_file.write_text(new_content)
            return True, "Successfully modified GDM config"
        else:
            return True, "Config already set correctly (no changes needed)"
    
    except PermissionError:
        return False, f"Permission denied. Run with sudo to modify {config_path}"
    except Exception as e:
        return False, f"Error modifying config: {e}"


def verify_changes(config_path: str) -> bool:
    """Verify that WaylandEnable=false is set in config."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return False
    
    try:
        content = config_file.read_text()
        in_daemon_section = False
        
        for line in content.split('\n'):
            stripped = line.strip()
            
            if stripped == '[daemon]':
                in_daemon_section = True
                continue
            
            if stripped.startswith('[') and stripped.endswith(']'):
                in_daemon_section = False
                continue
            
            if in_daemon_section:
                if 'WaylandEnable=false' in stripped and not stripped.startswith('#'):
                    return True
        
        return False
    
    except Exception:
        return False


def can_modify_config(config_path: str) -> bool:
    """Check if user has permissions to modify config file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return False
    
    # Check if file is writable
    if config_file.is_file() and os.access(config_path, os.W_OK):
        return True
    
    # Check if we can write with sudo
    # This is a heuristic - actual sudo check happens during modification
    return False


def convert_wayland_to_x11() -> Tuple[bool, str]:
    """Main function to convert Wayland to X11."""
    # Check current session type
    session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown').lower()
    if session_type == 'x11':
        return False, "Already running on X11 session"
    
    if session_type != 'wayland':
        return False, f"Unknown session type: {session_type}"
    
    # Detect distribution and display manager
    distro = detect_distribution()
    display_manager = detect_display_manager()
    
    if not display_manager:
        return False, "Could not detect display manager. Please configure manually."
    
    # Get config path
    config_path = get_config_path(display_manager, distro)
    if not config_path:
        return False, f"Could not find config file for {display_manager}"
    
    # Only GDM is supported for now
    if display_manager != 'gdm':
        return False, f"Display manager {display_manager} is not yet supported. Only GDM is supported."
    
    # Create backup
    backup_path = backup_config(config_path)
    if not backup_path:
        print("Warning: Could not create backup", file=sys.stderr)
    
    # Modify config
    success, message = modify_gdm_config(config_path)
    
    if success:
        # Verify changes
        if verify_changes(config_path):
            return True, f"Successfully disabled Wayland. Config file: {config_path}. Backup: {backup_path or 'none'}"
        else:
            return False, "Modification completed but verification failed. Please check config manually."
    else:
        return False, message


def main():
    """Main entry point."""
    success, message = convert_wayland_to_x11()
    
    if success:
        print(f"✓ {message}")
        print("\nNext steps:")
        print("1. Log out and log back in")
        print("2. Your system will use X11 session")
        print("3. draggg will work optimally")
        sys.exit(0)
    else:
        print(f"✗ {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
