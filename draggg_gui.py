#!/usr/bin/env python3
"""
draggg GUI - Main entry point for GUI setup and configuration tool.
"""

import sys
import tkinter as tk
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import config
    from gui.setup_wizard import SetupWizard
    from gui.settings_panel import SettingsPanel
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required dependencies are installed.")
    sys.exit(1)


def is_setup_complete() -> bool:
    """Check if initial setup has been completed."""
    config_file = config.DEFAULT_CONFIG_FILE
    
    if not config_file.exists():
        return False
    
    try:
        cfg = config.load_config()
        # Consider setup complete if config file exists and has valid data
        return bool(cfg)
    except Exception:
        return False


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    
    # Check if setup is needed
    if is_setup_complete():
        # Show settings panel
        app = SettingsPanel(root)
    else:
        # Show setup wizard
        app = SetupWizard(root)
    
    root.mainloop()


if __name__ == '__main__':
    main()

