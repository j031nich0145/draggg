#!/bin/bash
# Test script for GUI setup wizard
# This script helps test the GUI setup and configuration flow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "draggg GUI Setup Test Script"
echo "========================================="
echo ""

# Check if config exists
CONFIG_FILE="$HOME/.config/three-finger-drag/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠ Existing config found at: $CONFIG_FILE"
    echo "Would you like to:"
    echo "  1) Backup and test with fresh config (recommended for testing)"
    echo "  2) Continue with existing config (will show Settings Panel)"
    echo "  3) Cancel"
    read -p "Choice [1-3]: " choice
    
    case $choice in
        1)
            BACKUP="$CONFIG_FILE.backup.$(date +%s)"
            mv "$CONFIG_FILE" "$BACKUP"
            echo "✓ Config backed up to: $BACKUP"
            echo "  (GUI will show Setup Wizard)"
            ;;
        2)
            echo "✓ Using existing config"
            echo "  (GUI will show Settings Panel)"
            ;;
        3)
            echo "Cancelled"
            exit 0
            ;;
        *)
            echo "Invalid choice, cancelling"
            exit 1
            ;;
    esac
else
    echo "✓ No existing config found"
    echo "  (GUI will show Setup Wizard)"
fi

echo ""
echo "========================================="
echo "Launching GUI..."
echo "========================================="
echo ""
echo "Test Checklist:"
echo "  [ ] GUI window appears"
echo "  [ ] If Setup Wizard: All steps work (Next/Back buttons)"
echo "  [ ] If Settings Panel: All tabs accessible"
echo "  [ ] Sliders respond to input"
echo "  [ ] Settings save correctly"
echo "  [ ] Shortcut creation checkboxes work (in wizard final step)"
echo "  [ ] Service management buttons work (in Settings Panel)"
echo ""

# Launch GUI
python3 draggg_gui.py

echo ""
echo "========================================="
echo "GUI closed"
echo "========================================="
echo ""

# Verify config if it exists
if [ -f "$CONFIG_FILE" ]; then
    echo "Current configuration:"
    python3 -c "
import json
from pathlib import Path
config_file = Path('$CONFIG_FILE')
if config_file.exists():
    with open(config_file) as f:
        cfg = json.load(f)
    print(json.dumps(cfg, indent=2))
" 2>/dev/null || cat "$CONFIG_FILE"
fi

# Check desktop entry
DESKTOP_ENTRY="$HOME/.local/share/applications/draggg.desktop"
if [ -f "$DESKTOP_ENTRY" ]; then
    echo ""
    echo "Desktop entry installed at: $DESKTOP_ENTRY"
    echo "Icon setting: $(grep '^Icon=' "$DESKTOP_ENTRY" | cut -d= -f2)"
fi

# Check desktop shortcut
DESKTOP_SHORTCUT="$HOME/Desktop/draggg.desktop"
if [ -f "$DESKTOP_SHORTCUT" ]; then
    echo "Desktop shortcut found at: $DESKTOP_SHORTCUT"
fi

echo ""
echo "Test complete!"

