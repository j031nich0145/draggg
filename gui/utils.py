#!/usr/bin/env python3
"""
GUI utilities for draggg - Wayland detection, distribution detection, etc.
"""

import os
import subprocess
import platform
from typing import Dict, Optional, Tuple


def detect_session_type() -> str:
    """Detect current display server session type."""
    return os.environ.get('XDG_SESSION_TYPE', 'unknown').lower()


def is_wayland() -> bool:
    """Check if running on Wayland session."""
    return detect_session_type() == 'wayland'


def is_x11() -> bool:
    """Check if running on X11 session."""
    return detect_session_type() == 'x11'


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


def get_gdm_config_path() -> Optional[str]:
    """Get the GDM configuration file path for current distribution."""
    distro = detect_distribution()
    
    if distro in ('ubuntu', 'debian'):
        return '/etc/gdm3/custom.conf'
    elif distro == 'fedora':
        return '/etc/gdm/custom.conf'
    else:
        # Try common locations
        for path in ['/etc/gdm3/custom.conf', '/etc/gdm/custom.conf']:
            if os.path.exists(path):
                return path
    
    return None


def get_wayland_to_x11_instructions() -> Dict[str, str]:
    """Get instructions for switching from Wayland to X11 based on distribution."""
    distro = detect_distribution()
    config_path = get_gdm_config_path()
    
    instructions = {
        'method': 'config_file',
        'distro': distro,
        'config_file': config_path or '/etc/gdm3/custom.conf',
        'file_section': '[daemon]',
        'line_to_find': '#WaylandEnable=false',
        'line_to_set': 'WaylandEnable=false',
    }
    
    if distro in ('ubuntu', 'debian'):
        instructions['title'] = 'Ubuntu/Debian - Disable Wayland'
        instructions['description'] = (
            'Edit the GDM configuration file to disable Wayland:\n\n'
            f'1. Open: {config_path or "/etc/gdm3/custom.conf"}\n'
            '2. Find the [daemon] section\n'
            '3. Uncomment: #WaylandEnable=false → WaylandEnable=false\n'
            '4. Save the file\n'
            '5. Log out and log back in'
        )
    elif distro == 'fedora':
        instructions['title'] = 'Fedora - Disable Wayland'
        instructions['description'] = (
            'Edit the GDM configuration file to disable Wayland:\n\n'
            f'1. Open: {config_path or "/etc/gdm/custom.conf"}\n'
            '2. Find the [daemon] section\n'
            '3. Uncomment: #WaylandEnable=false → WaylandEnable=false\n'
            '4. Save the file\n'
            '5. Log out and log back in'
        )
    else:
        instructions['title'] = 'Disable Wayland'
        instructions['description'] = (
            'Edit the GDM configuration file to disable Wayland:\n\n'
            f'1. Open: {config_path or "/etc/gdm3/custom.conf"}\n'
            '2. Find the [daemon] section\n'
            '3. Uncomment: #WaylandEnable=false → WaylandEnable=false\n'
            '4. Save the file\n'
            '5. Log out and log back in'
        )
    
    return instructions


def get_logout_command() -> Optional[str]:
    """Get the appropriate logout command for the desktop environment."""
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    if 'gnome' in desktop:
        return 'gnome-session-quit --logout --no-prompt'
    elif 'kde' in desktop:
        return 'qdbus org.kde.ksmserver /KSMServer logout 0 0 0'
    elif 'xfce' in desktop:
        return 'xfce4-session-logout --logout'
    else:
        # Generic fallback - try common commands
        for cmd in ['gnome-session-quit --logout', 'loginctl terminate-user $USER']:
            try:
                subprocess.run(cmd.split(), check=False, capture_output=True, timeout=1)
                return cmd
            except:
                continue
    
    return None


def execute_logout() -> bool:
    """Execute logout command. Returns True if command was found and executed."""
    cmd = get_logout_command()
    if not cmd:
        return False
    
    try:
        # Use shell=True for commands with pipes or variables
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception:
        return False

