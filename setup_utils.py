#!/usr/bin/env python3
"""
Setup utilities - reusable functions for setup and configuration.
Extracted from setup.sh for use by both CLI and GUI.
"""

import os
import subprocess
import grp
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


def check_python_package(package_name: str) -> bool:
    """Check if a Python package is importable."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def check_command(command: str) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run(['which', command], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


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


def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are installed."""
    result = {
        'evdev': check_python_package('evdev'),
        'uinput': check_python_package('uinput'),
        'xdotool': check_command('xdotool'),
    }
    result['all_installed'] = all(result.values())
    return result


def get_package_manager_commands(distribution: str) -> Optional[Tuple[str, List[str]]]:
    """Get package manager command and package names for distribution."""
    distro = distribution.lower()
    
    if distro in ('ubuntu', 'debian'):
        return ('apt', ['python3-evdev', 'python3-uinput', 'xdotool', 'python3-xlib'])
    elif distro == 'fedora':
        return ('dnf', ['python3-evdev', 'python3-uinput', 'xdotool', 'python3-xlib'])
    elif distro == 'arch':
        return ('pacman', ['python-evdev', 'python-uinput', 'xdotool', 'python-xlib'])
    
    return None


def check_udev_rules() -> bool:
    """Check if udev rules for uinput are configured."""
    udev_rule = Path('/etc/udev/rules.d/99-uinput.rules')
    if not udev_rule.exists():
        return False
    
    try:
        content = udev_rule.read_text()
        return 'uinput' in content and 'MODE' in content
    except Exception:
        return False


def check_input_group() -> bool:
    """Check if current user is in 'input' group."""
    try:
        user_groups = [g.gr_name for g in grp.getgrall() if os.getlogin() in g.gr_mem]
        user_groups.append(grp.getgrgid(os.getgid()).gr_name)
        return 'input' in user_groups
    except Exception:
        return False


def check_service_status() -> Dict[str, Any]:
    """Check systemd service status."""
    result = {
        'exists': False,
        'enabled': False,
        'running': False,
        'error': None
    }
    
    try:
        # Check if service file exists
        service_file = Path.home() / '.config' / 'systemd' / 'user' / 'draggg.service'
        result['exists'] = service_file.exists()
        
        if result['exists']:
            # Check if enabled
            proc = subprocess.run(
                ['systemctl', '--user', 'is-enabled', 'draggg.service'],
                capture_output=True,
                text=True
            )
            result['enabled'] = proc.returncode == 0
            
            # Check if running
            proc = subprocess.run(
                ['systemctl', '--user', 'is-active', 'draggg.service'],
                capture_output=True,
                text=True
            )
            result['running'] = proc.returncode == 0
    except Exception as e:
        result['error'] = str(e)
    
    return result


def get_missing_dependencies() -> List[str]:
    """Get list of missing dependencies."""
    deps = check_dependencies()
    missing = []
    
    if not deps['evdev']:
        missing.append('python3-evdev')
    if not deps['uinput']:
        missing.append('python3-uinput')
    if not deps['xdotool']:
        missing.append('xdotool')
    
    return missing


def get_package_manager_commands(distribution: str) -> Optional[Tuple[str, List[str]]]:
    """Get package manager command and package names for distribution."""
    distro = distribution.lower()
    
    if distro in ('ubuntu', 'debian'):
        return ('apt', ['python3-evdev', 'python3-uinput', 'xdotool', 'python3-xlib'])
    elif distro == 'fedora':
        return ('dnf', ['python3-evdev', 'python3-uinput', 'xdotool', 'python3-xlib'])
    elif distro == 'arch':
        return ('pacman', ['python-evdev', 'python-uinput', 'xdotool', 'python-xlib'])
    
    return None

