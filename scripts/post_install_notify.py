#!/usr/bin/env python3
"""
Background post-installation notification handler for draggg.
Sends desktop notifications asking about PATH setup, desktop icon confirmation, and GUI launch.
"""

import os
import sys
import subprocess
import time
import traceback
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
log_dir = Path.home() / ".config" / "draggg"
log_file = log_dir / "post_install_notify.log"

def log_error(message: str, exception: Exception = None):
    """Log error to file."""
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
            if exception:
                f.write(traceback.format_exc() + "\n")
    except Exception:
        pass  # If logging fails, continue silently

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
    # Log import error but don't break pip install
    log_error(f"Import error: {e}", e)
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
    """Launch draggg-gui, handling PATH not being set yet."""
    try:
        # First try using the entry point (if PATH is set)
        try:
            subprocess.Popen(
                ["draggg-gui"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
        except FileNotFoundError:
            pass
        
        # Try python -m (works even if PATH not set)
        try:
            subprocess.Popen(
                [sys.executable, "-m", "draggg_gui"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
        except Exception:
            pass
        
        # Last resort: try to find the script directly
        try:
            scripts_dir = get_scripts_directory()
            if scripts_dir:
                gui_script = scripts_dir / "draggg-gui"
                if gui_script.exists():
                    subprocess.Popen(
                        [str(gui_script)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                    return True
        except Exception:
            pass
        
        return False
    except Exception as e:
        log_error(f"Error launching GUI: {e}", e)
        return False


def verify_notification_system() -> bool:
    """Verify that notification system is available."""
    try:
        # Check if notify-send is available
        result = subprocess.run(
            ["which", "notify-send"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            return True
        
        # Check if DISPLAY is set (for X11)
        if os.environ.get("DISPLAY"):
            return True
        
        # Check if WAYLAND_DISPLAY is set
        if os.environ.get("WAYLAND_DISPLAY"):
            return True
        
        return False
    except Exception:
        return False


def main():
    """Main function - send notifications and handle responses."""
    try:
        # Wait a moment for pip install to complete
        time.sleep(2)
        
        # Verify notification system is available
        if not verify_notification_system():
            log_error("Notification system not available (no DISPLAY/WAYLAND_DISPLAY or notify-send)")
            # Don't exit - try anyway, might work
            # sys.exit(0)  # Commented out to allow fallback attempts
        
        # Get icon path
        try:
            icon_path = get_icon_path()
            icon_str = str(icon_path) if icon_path else None
        except Exception as e:
            log_error(f"Error getting icon path: {e}", e)
            icon_str = None
        
        # First notification: PATH setup
        path_actions = {
            "yes": "Yes, add to PATH",
            "no": "Skip"
        }
        
        try:
            path_response = send_notification_with_response(
                title="draggg Installed Successfully!",
                message="Would you like to add draggg commands to your PATH?",
                actions=path_actions,
                icon=icon_str,
                timeout=60
            )
        except Exception as e:
            log_error(f"Error sending PATH notification: {e}", e)
            path_response = None
        
        if path_response == "yes":
            # Set up PATH
            try:
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
            except Exception as e:
                log_error(f"Error setting up PATH: {e}", e)
        
        # Wait a moment before second notification
        time.sleep(1)
        
        # Second notification: Desktop icon confirmation
        icon_actions = {
            "ok": "OK",
            "skip": "Skip"
        }
        
        try:
            icon_response = send_notification_with_response(
                title="draggg Desktop Integration",
                message="Desktop icon installed! You can find 'draggg' in your application menu.",
                actions=icon_actions,
                icon=icon_str,
                timeout=30
            )
        except Exception as e:
            log_error(f"Error sending icon notification: {e}", e)
            icon_response = None
        
        # Wait a moment before third notification
        time.sleep(1)
        
        # Third notification: Launch GUI
        gui_actions = {
            "yes": "Yes, open settings",
            "no": "Not now"
        }
        
        try:
            gui_response = send_notification_with_response(
                title="draggg Setup",
                message="Would you like to open the GUI to configure draggg settings now?",
                actions=gui_actions,
                icon=icon_str,
                timeout=60
            )
        except Exception as e:
            log_error(f"Error sending GUI notification: {e}", e)
            gui_response = None
        
        if gui_response == "yes":
            try:
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
                        message="Could not launch GUI. Run 'draggg-gui' manually or find it in your application menu.",
                        icon=icon_str,
                        timeout=5000
                    )
            except Exception as e:
                log_error(f"Error launching GUI: {e}", e)
    except Exception as e:
        log_error(f"Fatal error in main(): {e}", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Log error but don't break pip install
        log_error(f"Unhandled exception in post_install_notify: {e}", e)
        sys.exit(0)  # Exit cleanly
