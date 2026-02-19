#!/usr/bin/env python3
"""
Background post-installation notification handler for draggg.
Sends desktop notifications asking about PATH setup and GUI launch.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.desktop_notify import (
        send_notification_with_response,
        get_icon_path,
        send_notification
    )
    from scripts.post_install_setup import (
        get_scripts_directory,
        is_in_path,
        detect_shell,
        add_to_path
    )
except ImportError as e:
    # If imports fail, silently exit (don't break pip install)
    sys.exit(0)


def setup_path_non_interactive() -> bool:
    """Set up PATH non-interactively."""
    try:
        scripts_dir = get_scripts_directory()
        if not scripts_dir:
            return False
        
        # Check if already in PATH
        if is_in_path(scripts_dir):
            return True
        
        # Get shell and config file
        shell, config_file = detect_shell()
        
        # Add to PATH
        return add_to_path(shell, scripts_dir, config_file)
    except Exception:
        return False


def launch_gui() -> bool:
    """Launch draggg-gui."""
    try:
        # Try using the entry point
        subprocess.Popen(
            ["draggg-gui"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except FileNotFoundError:
        # Try python -m
        try:
            subprocess.Popen(
                [sys.executable, "-m", "draggg_gui"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
        except Exception:
            return False
    except Exception:
        return False


def main():
    """Main function - send notifications and handle responses."""
    # Wait a moment for pip install to complete
    time.sleep(2)
    
    # Get icon path
    icon_path = get_icon_path()
    icon_str = str(icon_path) if icon_path else None
    
    # First notification: PATH setup
    path_actions = {
        "yes": "Yes, add to PATH",
        "no": "Skip"
    }
    
    path_response = send_notification_with_response(
        title="draggg Installed Successfully!",
        message="Would you like to add draggg commands to your PATH?",
        actions=path_actions,
        icon=icon_str,
        timeout=60
    )
    
    if path_response == "yes":
        # Set up PATH
        if setup_path_non_interactive():
            send_notification(
                title="draggg",
                message="PATH configured successfully! Open a new terminal to use commands.",
                icon=icon_str,
                timeout=5000
            )
        else:
            send_notification(
                title="draggg",
                message="Could not configure PATH automatically. Run 'draggg-setup' to configure manually.",
                icon=icon_str,
                timeout=5000
            )
    
    # Wait a moment before second notification
    time.sleep(1)
    
    # Second notification: Launch GUI
    gui_actions = {
        "yes": "Yes, open settings",
        "no": "Not now"
    }
    
    gui_response = send_notification_with_response(
        title="draggg Setup",
        message="Would you like to open the GUI to configure draggg settings?",
        actions=gui_actions,
        icon=icon_str,
        timeout=60
    )
    
    if gui_response == "yes":
        if launch_gui():
            send_notification(
                title="draggg",
                message="Opening settings...",
                icon=icon_str,
                timeout=3000
            )
        else:
            send_notification(
                title="draggg",
                message="Could not launch GUI. Run 'draggg-gui' manually.",
                icon=icon_str,
                timeout=5000
            )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Silently fail - don't break pip install
        pass
