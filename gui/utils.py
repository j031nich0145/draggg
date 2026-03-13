#!/usr/bin/env python3
"""
GUI utilities for draggg - Wayland detection, distribution detection, etc.
"""
from __future__ import annotations

import os
import subprocess
import platform


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


def detect_display_manager() -> Optional[str]:
    """Detect active display manager."""
    import subprocess
    from pathlib import Path
    
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


def can_modify_config(config_path: Optional[str] = None) -> bool:
    """Check if user has permissions to modify config file."""
    from pathlib import Path
    
    if not config_path:
        distro = detect_distribution()
        dm = detect_display_manager()
        if not dm:
            return False
        # Get config path based on DM and distro
        if dm == 'gdm':
            config_path = get_gdm_config_path()
        elif dm == 'lightdm':
            config_path = '/etc/lightdm/lightdm.conf'
        elif dm == 'sddm':
            config_path = '/etc/sddm.conf'
        else:
            return False
        
        if not config_path:
            return False
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        return False
    
    # Check if file is writable
    if config_file.is_file() and os.access(config_path, os.W_OK):
        return True
    
    # Check if we can write with sudo
    # This is a heuristic - actual sudo check happens during modification
    return False


def modify_wayland_config() -> Tuple[bool, str]:
    """Wrapper to call wayland_to_x11 conversion script."""
    import sys
    import subprocess
    from pathlib import Path
    
    # Get script path
    script_path = Path(__file__).parent.parent / 'scripts' / 'wayland_to_x11.py'
    if not script_path.exists():
        return False, "Conversion script not found"
    
    try:
        # Run script as subprocess
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip() or result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Conversion script timed out"
    except Exception as e:
        return False, f"Error running conversion script: {e}"

