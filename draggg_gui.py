#!/usr/bin/env python3
"""
draggg GUI - Main entry point for GUI setup and configuration tool.
"""

import sys
import os
from pathlib import Path

# Detect if running from source (development) vs installed package
# When installed, __file__ points to the installed package location
# When running from source, __file__ is in the source directory
def _is_development_mode():
    """Check if running from source directory (development mode)."""
    file_path = Path(__file__).resolve()
    # Check if we're in a source directory (has setup.py, README.md, etc.)
    source_indicators = ['setup.py', 'README.md', 'draggg.py']
    parent_dir = file_path.parent
    return any((parent_dir / indicator).exists() for indicator in source_indicators)

# Only add to sys.path if running from source (development mode)
# When installed as a package, imports should work without path manipulation
if _is_development_mode():
    sys.path.insert(0, str(Path(__file__).parent))

# Check if running from desktop file (no TTY)
_is_desktop_launch = not sys.stdout.isatty()

# Error logging setup
_log_file = None
if _is_desktop_launch:
    try:
        log_dir = Path.home() / '.config' / 'draggg'
        log_dir.mkdir(parents=True, exist_ok=True)
        _log_file = log_dir / 'gui_error.log'
    except Exception:
        pass  # Fail silently if can't create log file

def _log_error(message):
    """Log error to file and optionally print."""
    if _log_file:
        try:
            with open(_log_file, 'a') as f:
                from datetime import datetime
                f.write(f"[{datetime.now()}] {message}\n")
        except Exception:
            pass
    if not _is_desktop_launch:
        print(message, file=sys.stderr)

def _show_error_dialog(title, message):
    """Show error dialog using tkinter messagebox."""
    try:
        # Import here to avoid circular dependency
        import tkinter
        import tkinter.messagebox as msgbox
        root = tkinter.Tk()
        root.withdraw()  # Hide main window
        msgbox.showerror(title, message)
        root.destroy()
    except Exception as e:
        # Fallback if tkinter fails
        _log_error(f"Could not show error dialog: {e}")
        _log_error(f"Original error: {title}: {message}")

# Check DISPLAY environment variable before importing tkinter
if 'DISPLAY' not in os.environ and os.name != 'nt':
    error_msg = (
        "DISPLAY environment variable is not set.\n\n"
        "This GUI application requires an X11 display server.\n"
        "Please ensure you are running in a graphical environment.\n\n"
        "If you're using SSH, use X11 forwarding:\n"
        "  ssh -X user@host\n\n"
        "Or set DISPLAY manually:\n"
        "  export DISPLAY=:0"
    )
    _log_error(error_msg)
    if _is_desktop_launch:
        # Try to show error dialog (may fail if DISPLAY is truly missing)
        try:
            import tkinter
            _show_error_dialog("Display Error", error_msg)
        except Exception:
            pass
    else:
        print(error_msg, file=sys.stderr)
    sys.exit(1)

# Import tkinter with error handling
try:
    import tkinter as tk
    import tkinter.messagebox as messagebox
except ImportError as e:
    error_msg = (
        f"Failed to import tkinter: {e}\n\n"
        "tkinter is required for the GUI but is not available.\n\n"
        "Install it with:\n"
        "  Ubuntu/Debian: sudo apt install python3-tk\n"
        "  Fedora: sudo dnf install python3-tkinter\n"
        "  Arch: sudo pacman -S tk\n"
        "  macOS: tkinter is usually included with Python\n"
        "  Windows: tkinter is usually included with Python"
    )
    _log_error(error_msg)
    if _is_desktop_launch:
        # Can't show dialog without tkinter, but try to log
        _log_error("Cannot show error dialog - tkinter is missing")
    else:
        print(error_msg, file=sys.stderr)
    sys.exit(1)

# Import application modules with improved error handling
try:
    import config
except ImportError as e:
    error_msg = (
        f"Failed to import config module: {e}\n\n"
        "This may indicate an incomplete installation.\n\n"
        "If you installed via pip, try:\n"
        "  pip install --force-reinstall draggg\n\n"
        "If running from source, ensure all files are present."
    )
    _log_error(error_msg)
    if _is_desktop_launch:
        _show_error_dialog("Import Error", error_msg)
    else:
        print(error_msg, file=sys.stderr)
    sys.exit(1)

try:
    from gui.setup_wizard import SetupWizard
    from gui.settings_panel import SettingsPanel
except ImportError as e:
    error_msg = (
        f"Failed to import GUI modules: {e}\n\n"
        "This may indicate an incomplete installation.\n\n"
        "Missing module: " + str(e).split("'")[1] if "'" in str(e) else str(e) + "\n\n"
        "If you installed via pip, try:\n"
        "  pip install --force-reinstall draggg\n\n"
        "If running from source, ensure the 'gui' directory is present."
    )
    _log_error(error_msg)
    if _is_desktop_launch:
        _show_error_dialog("Import Error", error_msg)
    else:
        print(error_msg, file=sys.stderr)
    sys.exit(1)


def is_setup_complete() -> bool:
    """Check if initial setup has been completed."""
    try:
        config_file = config.DEFAULT_CONFIG_FILE
        
        if not config_file.exists():
            return False
        
        cfg = config.load_config()
        # Consider setup complete if config file exists and has valid data
        return bool(cfg)
    except Exception as e:
        _log_error(f"Error checking setup status: {e}")
        return False


def main():
    """Main entry point for GUI application."""
    try:
        root = tk.Tk()
        
        # Set window title
        root.title("draggg - Three-Finger Drag Configuration")
        
        # Check if setup is needed
        if is_setup_complete():
            # Show settings panel
            app = SettingsPanel(root)
        else:
            # Show setup wizard
            app = SetupWizard(root)
        
        root.mainloop()
        
    except tk.TclError as e:
        error_msg = (
            f"Tkinter error: {e}\n\n"
            "This may indicate a display server issue.\n\n"
            "Common causes:\n"
            "  - DISPLAY environment variable not set correctly\n"
            "  - X11 server not running\n"
            "  - Insufficient permissions\n\n"
            "Check your display configuration and try again."
        )
        _log_error(error_msg)
        if _is_desktop_launch:
            try:
                _show_error_dialog("Display Error", error_msg)
            except Exception:
                pass  # Can't show dialog if tkinter is broken
        else:
            print(error_msg, file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        error_msg = (
            f"Unexpected error starting GUI: {type(e).__name__}: {e}\n\n"
            "Please check the error log for details:\n"
            f"  {_log_file if _log_file else '~/.config/draggg/gui_error.log'}\n\n"
            "If the problem persists, try:\n"
            "  pip install --force-reinstall draggg"
        )
        _log_error(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        _log_error(traceback.format_exc())
        if _is_desktop_launch:
            try:
                _show_error_dialog("Error", error_msg)
            except Exception:
                pass
        else:
            print(error_msg, file=sys.stderr)
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
