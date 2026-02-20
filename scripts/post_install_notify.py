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
        add_to_path,
        check_wayland
    )
except ImportError as e:
    # Log import error but don't break pip install
    log_error(f"Import error: {e}", e)
    sys.exit(0)

# Try to import curses for TUI fallback
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    CURSES_AVAILABLE = False


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


def show_tui_prompt(title: str, message: str, options: list) -> str:
    """
    Show a TUI prompt using curses as fallback for notifications.
    
    Args:
        title: Prompt title
        message: Prompt message
        options: List of (key, label) tuples, e.g., [("y", "Yes"), ("n", "No")]
    
    Returns:
        Selected key or None if cancelled
    """
    if not CURSES_AVAILABLE:
        return None
    
    try:
        # Use curses wrapper for proper cleanup
        def _show_prompt(stdscr):
            curses.curs_set(0)  # Hide cursor
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Title
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Selected
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Highlight
            
            height, width = stdscr.getmaxyx()
            selected = 0
            
            while True:
                stdscr.clear()
                
                # Title
                stdscr.addstr(0, 0, title, curses.color_pair(1) | curses.A_BOLD)
                
                # Message (wrap if needed)
                msg_lines = message.split('\n')
                y = 2
                for line in msg_lines:
                    if y >= height - len(options) - 2:
                        break
                    stdscr.addstr(y, 0, line[:width-1])
                    y += 1
                
                y += 1
                
                # Options
                for idx, (key, label) in enumerate(options):
                    if y >= height - 1:
                        break
                    prefix = "> " if idx == selected else "  "
                    color = curses.color_pair(3) if idx == selected else curses.color_pair(0)
                    stdscr.addstr(y, 0, f"{prefix}[{key}] {label}", color)
                    y += 1
                
                stdscr.refresh()
                
                # Handle input
                key = stdscr.getch()
                if key == curses.KEY_UP:
                    selected = (selected - 1) % len(options)
                elif key == curses.KEY_DOWN:
                    selected = (selected + 1) % len(options)
                elif key == ord('\n') or key == ord('\r'):
                    return options[selected][0]
                elif key == 27:  # ESC
                    return None
                else:
                    # Check if key matches an option
                    for idx, (opt_key, _) in enumerate(options):
                        if key == ord(opt_key.lower()) or key == ord(opt_key.upper()):
                            return opt_key
        
        return curses.wrapper(_show_prompt)
    except Exception as e:
        log_error(f"Error showing TUI prompt: {e}", e)
        return None


def launch_wayland_conversion() -> bool:
    """Launch Wayland to X11 conversion TUI."""
    try:
        # Try using the entry point
        try:
            subprocess.Popen(
                ["wayland-to-x11-tui"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            return True
        except FileNotFoundError:
            pass
        
        # Try python -m
        try:
            subprocess.Popen(
                [sys.executable, "-m", "scripts.wayland_to_x11_tui"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            return True
        except Exception:
            pass
        
        # Last resort: try to find the script directly
        try:
            scripts_dir = get_scripts_directory()
            if scripts_dir:
                wayland_script = scripts_dir / "wayland-to-x11-tui"
                if wayland_script.exists():
                    subprocess.Popen(
                        [str(wayland_script)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True
                    )
                    return True
        except Exception:
            pass
        
        return False
    except Exception as e:
        log_error(f"Error launching Wayland conversion: {e}", e)
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
        
        path_response = None
        use_tui = False
        
        try:
            path_response = send_notification_with_response(
                title="draggg Installed Successfully!",
                message="Would you like to add draggg commands to your PATH?",
                actions=path_actions,
                icon=icon_str,
                timeout=60
            )
            # If no response, try TUI fallback
            if path_response is None:
                use_tui = True
                log_error("No response from PATH notification, using TUI fallback")
        except Exception as e:
            log_error(f"Error sending PATH notification: {e}", e)
            use_tui = True
        
        # TUI fallback for PATH
        if use_tui or path_response is None:
            try:
                path_response = show_tui_prompt(
                    "draggg Installed Successfully!",
                    "Would you like to add draggg commands to your PATH?\n\nScripts are installed in ~/.local/bin",
                    [("y", "Yes, add to PATH"), ("n", "Skip")]
                )
                if path_response == "y":
                    path_response = "yes"
                elif path_response == "n":
                    path_response = "no"
            except Exception as e:
                log_error(f"Error showing TUI prompt: {e}", e)
                path_response = None
        
        if path_response == "yes":
            # Set up PATH
            try:
                if setup_path_non_interactive():
                    if not use_tui:
                        send_notification(
                            title="draggg",
                            message="PATH configured successfully! Open a new terminal to use commands.",
                            icon=icon_str,
                            timeout=5000
                        )
                    else:
                        # TUI mode - just log
                        log_error("PATH configured successfully via TUI")
                else:
                    if not use_tui:
                        send_notification(
                            title="draggg",
                            message="Could not configure PATH automatically. Run 'draggg-setup' to configure manually.",
                            icon=icon_str,
                            timeout=5000
                        )
                    else:
                        log_error("Could not configure PATH automatically via TUI")
            except Exception as e:
                log_error(f"Error setting up PATH: {e}", e)
        
        # Wait a moment before second notification
        time.sleep(1)
        
        # Check for Wayland and offer conversion
        wayland_response = None
        if check_wayland():
            wayland_actions = {
                "yes": "Yes, convert to X11",
                "no": "Skip"
            }
            
            try:
                wayland_response = send_notification_with_response(
                    title="draggg - Wayland Detected",
                    message="You're running Wayland. draggg works best with X11. Convert to X11 now?",
                    actions=wayland_actions,
                    icon=icon_str,
                    timeout=60
                )
                if wayland_response is None:
                    # TUI fallback
                    wayland_response = show_tui_prompt(
                        "draggg - Wayland Detected",
                        "You're running Wayland. draggg works best with X11.\n\nConvert to X11 now?",
                        [("y", "Yes, convert to X11"), ("n", "Skip")]
                    )
                    if wayland_response == "y":
                        wayland_response = "yes"
                    elif wayland_response == "n":
                        wayland_response = "no"
            except Exception as e:
                log_error(f"Error sending Wayland notification: {e}", e)
                # TUI fallback
                try:
                    wayland_response = show_tui_prompt(
                        "draggg - Wayland Detected",
                        "You're running Wayland. draggg works best with X11.\n\nConvert to X11 now?",
                        [("y", "Yes, convert to X11"), ("n", "Skip")]
                    )
                    if wayland_response == "y":
                        wayland_response = "yes"
                    elif wayland_response == "n":
                        wayland_response = "no"
                except Exception as e2:
                    log_error(f"Error showing Wayland TUI prompt: {e2}", e2)
            
            if wayland_response == "yes":
                try:
                    if launch_wayland_conversion():
                        if not use_tui:
                            send_notification(
                                title="draggg",
                                message="Launching Wayland to X11 conversion helper...",
                                icon=icon_str,
                                timeout=3000
                            )
                    else:
                        if not use_tui:
                            send_notification(
                                title="draggg",
                                message="Could not launch conversion helper. Run 'wayland-to-x11-tui' manually.",
                                icon=icon_str,
                                timeout=5000
                            )
                except Exception as e:
                    log_error(f"Error launching Wayland conversion: {e}", e)
            
            time.sleep(1)
        
        # Second notification: Desktop icon confirmation (skip if using TUI)
        if not use_tui:
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
        
        # Wait a moment before third notification
        time.sleep(1)
        
        # Third notification: Launch GUI
        gui_actions = {
            "yes": "Yes, open settings",
            "no": "Not now"
        }
        
        gui_response = None
        try:
            if not use_tui:
                gui_response = send_notification_with_response(
                    title="draggg Setup",
                    message="Would you like to open the GUI to configure draggg settings now?",
                    actions=gui_actions,
                    icon=icon_str,
                    timeout=60
                )
            
            # TUI fallback for GUI prompt
            if gui_response is None:
                gui_response = show_tui_prompt(
                    "draggg Setup",
                    "Would you like to open the GUI to configure draggg settings now?",
                    [("y", "Yes, open settings"), ("n", "Not now")]
                )
                if gui_response == "y":
                    gui_response = "yes"
                elif gui_response == "n":
                    gui_response = "no"
        except Exception as e:
            log_error(f"Error sending GUI notification: {e}", e)
            # TUI fallback
            try:
                gui_response = show_tui_prompt(
                    "draggg Setup",
                    "Would you like to open the GUI to configure draggg settings now?",
                    [("y", "Yes, open settings"), ("n", "Not now")]
                )
                if gui_response == "y":
                    gui_response = "yes"
                elif gui_response == "n":
                    gui_response = "no"
            except Exception as e2:
                log_error(f"Error showing GUI TUI prompt: {e2}", e2)
        
        if gui_response == "yes":
            try:
                if launch_gui():
                    if not use_tui:
                        send_notification(
                            title="draggg",
                            message="Opening settings...",
                            icon=icon_str,
                            timeout=3000
                        )
                    else:
                        log_error("GUI launched successfully via TUI")
                else:
                    if not use_tui:
                        send_notification(
                            title="draggg",
                            message="Could not launch GUI. Run 'draggg-gui' manually or find it in your application menu.",
                            icon=icon_str,
                            timeout=5000
                        )
                    else:
                        log_error("Could not launch GUI via TUI")
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
