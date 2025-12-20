# Linux Three-Finger Drag

A Linux implementation of macOS-style three-finger drag for touchpads. This tool enables natural dragging gestures using three fingers on your trackpad, providing a smooth and intuitive way to move windows, select text, and interact with UI elements.

## Features

- **macOS-style three-finger drag**: Natural dragging gestures with three fingers
- **Multi-touchpad support**: Works with Apple trackpads and standard Linux touchpads
- **Automatic hardware detection**: Automatically finds and configures your touchpad
- **Customizable sensitivity**: Adjust drag sensitivity and movement thresholds
- **Left-handed support**: Configurable for left-handed users
- **Background service**: Optional systemd service for always-on operation
- **X11 and Wayland compatible**: Works with both display server protocols

## Prerequisites

### System Requirements

- **Linux distribution**: Ubuntu, Debian, Fedora, Arch Linux, or compatible
- **Python 3.8+**: Python 3.8 or higher required
- **Display server**: X11 recommended (Wayland supported but may have limitations)
- **Touchpad**: Multi-touch capable touchpad (Apple trackpad, Synaptics, or libinput)

### Required System Packages

The installation script will help you install these, but here's what's needed:

**Ubuntu/Debian:**
```bash
sudo apt install python3-evdev python3-uinput xdotool python3-xlib
```

**Fedora:**
```bash
sudo dnf install python3-evdev python3-uinput xdotool python3-xlib
```

**Arch Linux:**
```bash
sudo pacman -S python-evdev python-uinput xdotool python-xlib
```

### Permissions

The tool requires access to input devices. You have two options:

1. **Run with sudo** (quick but less secure)
2. **Add user to input group and configure udev rules** (recommended, handled by setup script)

## Quick Start

### Automated Installation (Recommended)

1. **Clone or download this repository:**
   ```bash
   cd Linux_Three_Fingers
   ```

2. **Run the interactive setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   The setup script will:
   - Check system compatibility
   - Detect your touchpad hardware
   - Install dependencies (with your confirmation)
   - Set up permissions
   - Configure settings interactively
   - Optionally install as a systemd service

3. **Run the application:**
   ```bash
   # If installed as service, it should already be running
   # Otherwise, run manually:
   sudo python3 three_finger_drag.py
   # Or if permissions are configured:
   python3 three_finger_drag.py
   ```

### Manual Installation

If you prefer manual setup:

1. **Install dependencies** (see Prerequisites above)

2. **Set up permissions** (choose one):

   **Option A: Run with sudo** (simple but requires sudo each time)
   
   **Option B: Configure udev rules** (recommended):
   ```bash
   # Create udev rule for uinput access
   sudo bash -c 'echo KERNEL==\"uinput\", MODE=\"0666\" > /etc/udev/rules.d/99-uinput.rules'
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   
   # Add user to input group
   sudo usermod -a -G input $USER
   # Log out and back in for group changes to take effect
   ```

3. **Find your touchpad device:**
   ```bash
   python3 detect_hardware.py
   ```

4. **Run with device path:**
   ```bash
   python3 three_finger_drag.py --device /dev/input/eventX
   ```

## Usage

### Basic Usage

```bash
# Automatic device detection
python3 three_finger_drag.py

# Specify device manually
python3 three_finger_drag.py --device /dev/input/event5

# Use configuration file
python3 three_finger_drag.py --config ~/.config/three-finger-drag/config.json

# Verbose logging
python3 three_finger_drag.py --verbose
```

### Command-Line Options

```
--device PATH          Specify touchpad device path manually
--threshold N          Movement threshold in pixels (default: 10)
--drag-sensitivity F   Drag sensitivity multiplier (default: 1.0)
--left-handed          Use rightmost finger for left-handed users
--leading-weight F     Weight for leading finger (default: 1.5)
--other-weight F       Weight for other fingers (default: 0.3)
--config PATH          Path to configuration file
--verbose, -v          Enable verbose/debug logging
```

### Configuration File

Create a configuration file at `~/.config/three-finger-drag/config.json`:

```json
{
  "device": "/dev/input/event5",
  "threshold": 10,
  "drag_sensitivity": 1.0,
  "left_handed": false,
  "leading_finger_weight": 1.5,
  "other_fingers_weight": 0.3
}
```

Command-line arguments override configuration file settings.

### Running as a Systemd Service

If installed via setup script, the service is already configured. Otherwise:

1. **Copy service file:**
   ```bash
   cp three-finger-drag.service ~/.config/systemd/user/
   ```

2. **Edit the service file** to set correct paths

3. **Enable and start:**
   ```bash
   systemctl --user enable three-finger-drag.service
   systemctl --user start three-finger-drag.service
   ```

4. **Check status:**
   ```bash
   systemctl --user status three-finger-drag.service
   ```

## Hardware Compatibility

### Supported Touchpads

- **Apple Trackpads** (bcm5974 driver): Full support
- **Synaptics touchpads**: Full support
- **libinput touchpads**: Full support
- **Multi-touch trackpads**: Any touchpad with multi-touch capabilities

### Detection

The tool automatically detects touchpads by checking for:
- Multi-touch slot capability (ABS_MT_SLOT)
- Tracking ID capability (ABS_MT_TRACKING_ID)
- Position axes (ABS_MT_POSITION_X/Y or ABS_X/Y)

Use `detect_hardware.py` to see all available input devices and their compatibility.

## Troubleshooting

### Touchpad Not Detected

1. **Check permissions:**
   ```bash
   ls -l /dev/input/event*
   # Your user should have read access, or be in 'input' group
   ```

2. **Run hardware detection:**
   ```bash
   python3 detect_hardware.py
   ```

3. **Try running with sudo:**
   ```bash
   sudo python3 three_finger_drag.py
   ```

### Permission Denied for /dev/uinput

1. **Check udev rules:**
   ```bash
   cat /etc/udev/rules.d/99-uinput.rules
   ```

2. **Verify group membership:**
   ```bash
   groups
   # Should include 'input'
   ```

3. **Reload udev rules:**
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

4. **Log out and back in** if you were just added to the input group

### Gestures Not Working

1. **Check session type:**
   ```bash
   echo $XDG_SESSION_TYPE
   # Should be 'x11' for best compatibility
   ```

2. **Enable verbose logging:**
   ```bash
   python3 three_finger_drag.py --verbose
   ```

3. **Verify touchpad detection:**
   - Check that the correct device is being used
   - Verify three fingers are detected (check logs)

4. **Adjust sensitivity:**
   ```bash
   python3 three_finger_drag.py --drag-sensitivity 1.5
   ```

### Cursor Position Issues

1. **Install xdotool:**
   ```bash
   sudo apt install xdotool  # Ubuntu/Debian
   sudo dnf install xdotool  # Fedora
   ```

2. **Or install python-xlib as fallback:**
   ```bash
   sudo apt install python3-xlib
   ```

The tool will fall back to relative movement if cursor position cannot be determined.

### Wayland Issues

Wayland support is limited. For best results:
- Switch to X11 session if possible
- Or the tool will use relative movement mode (may feel less precise)

## Configuration Options

### Movement Threshold

The `threshold` parameter controls how far your fingers must move before dragging starts (in pixels). Lower values make it more sensitive.

**Recommended:** 5-15 pixels

### Drag Sensitivity

The `drag_sensitivity` multiplier affects how cursor movement relates to finger movement. Higher values = more cursor movement per finger movement.

**Recommended:** 0.5-2.0

### Finger Weights

- **leading_weight**: Weight for the leading finger (leftmost for right-handed, rightmost for left-handed)
- **other_weight**: Weight for the other two fingers

These affect how finger positions are averaged. Higher leading weight makes the leading finger more influential.

**Recommended:** leading_weight 1.0-2.0, other_weight 0.2-0.5

## Technical Details

### How It Works

1. **Event Detection**: Listens to raw input events from the touchpad via evdev
2. **Finger Tracking**: Tracks multiple touch points using multi-touch slot events
3. **Gesture Recognition**: Detects when exactly three fingers are on the touchpad
4. **Cursor Locking**: Locks cursor position and tracks relative finger movement
5. **Mouse Simulation**: Emulates mouse button press and movement via uinput

### Architecture

- **Input**: Reads from `/dev/input/eventX` (touchpad device)
- **Output**: Writes to `/dev/uinput` (virtual mouse device)
- **Cursor Position**: Uses xdotool or X11 API for absolute positioning

### Dependencies

- **python3-evdev**: Linux input event device access
- **python3-uinput**: Virtual input device creation
- **xdotool**: Cursor position queries (optional, X11 API fallback available)

## Contributing

Contributions welcome! Areas for improvement:
- Additional touchpad driver support
- Wayland improvements
- Gesture customization
- Performance optimizations

## License

[Add your license here]

## Acknowledgments

Built with:
- [python-evdev](https://github.com/gvalkov/python-evdev) - Linux input event handling
- [python-uinput](https://github.com/tuomasjjrasanen/python-uinput) - Virtual input device support

