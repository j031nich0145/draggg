# draggg - Linux Three-Finger Drag

A Linux implementation of macOS-style three-finger drag for touchpads. This tool enables natural dragging gestures using three fingers on your trackpad, providing a smooth and intuitive way to move windows, select text, and interact with UI elements.

## Features

- **macOS-style three-finger drag**: Natural dragging gestures with three fingers
- **Intelligent finger tracking**: Weighted position tracking with leading finger emphasis
- **Multi-touchpad support**: Works with Apple trackpads and standard Linux touchpads
- **Automatic hardware detection**: Automatically finds and configures your touchpad
- **Customizable sensitivity**: Adjust drag sensitivity and movement thresholds
- **Left-handed support**: Configurable for left-handed users
- **Background service**: Optional systemd service for always-on operation
- **X11 compatible**: Works with X11 display server (recommended)

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

### Option 1: Automated Installation (Recommended)

1. **Clone or download this repository:**
   ```bash
   cd draggg
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
   sudo python3 draggg.py
   # Or if permissions are configured:
   python3 draggg.py
   ```

### Option 2: Manual Build and Setup

For detailed step-by-step instructions on building from source, testing, and setting up as a background service, see the **[Building and Testing](#building-and-testing)** section below.

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
   python3 draggg.py --device /dev/input/eventX
   ```

## Building and Testing

### Step 1: Build and Install

1. **Clone or download the repository:**
   ```bash
   git clone <repository-url>
   cd draggg
   # Or if you already have the files:
   cd draggg
   ```

2. **Install system dependencies:**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
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

3. **Set up permissions (choose one method):**

   **Method A: Add user to input group (recommended):**
   ```bash
   # Add udev rule for uinput access
   echo 'KERNEL=="uinput", MODE="0666"' | sudo tee /etc/udev/rules.d/99-uinput.rules
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   
   # Add user to input group
   sudo usermod -a -G input $USER
   ```
   
   **Important:** You must log out and log back in for group changes to take effect.
   
   **Method B: Run with sudo (for testing only):**
   ```bash
   # You can test with sudo, but it's not recommended for production use
   sudo python3 draggg.py
   ```

### Step 2: Test as a User

1. **Detect your touchpad:**
   ```bash
   python3 detect_hardware.py
   ```
   
   This will show you:
   - Compatible touchpads on your system
   - Device paths (e.g., `/dev/input/event5`)
   - Permission status

2. **Test the script manually:**
   
   **With auto-detection:**
   ```bash
   python3 draggg.py
   ```
   
   **With specific device:**
   ```bash
   python3 draggg.py --device /dev/input/event5
   ```
   
   **With verbose logging (recommended for first test):**
   ```bash
   python3 draggg.py --verbose
   ```

3. **Test the gesture:**
   - Place three fingers on your trackpad
   - Move them together (the cursor should move and drag)
   - Lift your fingers (the drag should release)
   
   You should see log output indicating:
   - Device detection
   - Three-finger detection
   - Drag state changes

4. **Stop the test:**
   - Press `Ctrl+C` to stop the script

### Step 3: Configure Settings (Optional)

Create a configuration file for persistent settings:

```bash
mkdir -p ~/.config/three-finger-drag
```

Edit `~/.config/three-finger-drag/config.json`:

```json
{
  "device": "/dev/input/event5",
  "threshold": 10,
  "drag_sensitivity": 0.25,
  "left_handed": false,
  "leading_finger_weight": 1.5,
  "other_fingers_weight": 0.3
}
```

Replace `/dev/input/event5` with your actual device path from Step 2.

### Step 4: Set Up as Background Service (Boot-Time Startup)

To have draggg automatically start on boot and run in the background:

1. **Locate your installation directory:**
   ```bash
   # Note the full path to your draggg directory
   pwd
   # Example output: /home/username/draggg
   ```

2. **Copy and edit the service file:**
   ```bash
   # Create systemd user service directory
   mkdir -p ~/.config/systemd/user
   
   # Copy the service file
   cp draggg.service ~/.config/systemd/user/
   
   # Edit the service file with your actual paths
   nano ~/.config/systemd/user/draggg.service
   # Or use your preferred editor: vim, gedit, etc.
   ```

3. **Update the service file:**
   
   Edit `~/.config/systemd/user/draggg.service` and change these lines:
   
   ```ini
   [Service]
   Type=simple
   # Replace /path/to/draggg with your actual installation path
   ExecStart=/usr/bin/python3 /home/username/draggg/draggg.py
   # Or with config file:
   # ExecStart=/usr/bin/python3 /home/username/draggg/draggg.py --config %h/.config/three-finger-drag/config.json
   ```
   
   **Important:** 
   - Replace `/home/username/draggg` with your actual path
   - Use `which python3` to find your Python 3 path if `/usr/bin/python3` doesn't work
   - The `%h` in the config path is a systemd variable that expands to your home directory

4. **Enable and start the service:**
   ```bash
   # Reload systemd to recognize the new service
   systemctl --user daemon-reload
   
   # Enable the service to start on boot
   systemctl --user enable draggg.service
   
   # Start the service now (without rebooting)
   systemctl --user start draggg.service
   ```

5. **Verify the service is running:**
   ```bash
   # Check service status
   systemctl --user status draggg.service
   ```
   
   You should see:
   - `Active: active (running)`
   - Recent log entries showing device detection

6. **View service logs:**
   ```bash
   # View recent logs
   journalctl --user -u draggg.service -n 50
   
   # Follow logs in real-time
   journalctl --user -u draggg.service -f
   ```

7. **Test the gesture:**
   - The service should now be running in the background
   - Test the three-finger drag gesture
   - Check logs if it's not working: `journalctl --user -u draggg.service -f`

### Service Management Commands

**Stop the service:**
```bash
systemctl --user stop draggg.service
```

**Start the service:**
```bash
systemctl --user start draggg.service
```

**Restart the service (after configuration changes):**
```bash
systemctl --user restart draggg.service
```

**Disable auto-start on boot:**
```bash
systemctl --user disable draggg.service
```

**Check if service is enabled:**
```bash
systemctl --user is-enabled draggg.service
```

**View service logs:**
```bash
# Last 100 lines
journalctl --user -u draggg.service -n 100

# Follow in real-time
journalctl --user -u draggg.service -f

# Since boot
journalctl --user -u draggg.service --since boot
```

### Troubleshooting the Service

**Service won't start:**
1. Check the service file paths are correct
2. Verify Python 3 path: `which python3`
3. Check logs: `journalctl --user -u draggg.service -n 50`
4. Test manually: `python3 draggg.py` to see error messages

**Service starts but gestures don't work:**
1. Check permissions: `groups` (should include 'input')
2. Verify device path in config matches your touchpad
3. Check logs for errors: `journalctl --user -u draggg.service -f`
4. Test with verbose mode manually to see what's happening

**Service doesn't start on boot:**
1. Verify it's enabled: `systemctl --user is-enabled draggg.service`
2. Check if systemd user services are enabled: `systemctl --user list-unit-files | grep draggg`
3. Ensure you're logged in to a graphical session (X11)

**Permission errors:**
1. Make sure you logged out and back in after adding to 'input' group
2. Verify udev rules: `cat /etc/udev/rules.d/99-uinput.rules`
3. Reload udev: `sudo udevadm control --reload-rules && sudo udevadm trigger`

## Usage

### Basic Usage

```bash
# Automatic device detection
python3 draggg.py

# Specify device manually
python3 draggg.py --device /dev/input/event5

# Use configuration file
python3 draggg.py --config ~/.config/three-finger-drag/config.json

# Verbose logging
python3 draggg.py --verbose
```

### Command-Line Options

```
--device PATH          Specify touchpad device path manually
--threshold N          Movement threshold in pixels (default: 10)
--drag-sensitivity F   Drag sensitivity multiplier (default: 0.25)
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
  "drag_sensitivity": 0.25,
  "left_handed": false,
  "leading_finger_weight": 1.5,
  "other_fingers_weight": 0.3
}
```

Command-line arguments override configuration file settings.

### Running as a Systemd Service

For detailed step-by-step instructions on building, testing, and setting up draggg as a background service that starts on boot, see the **[Building and Testing](#building-and-testing)** section above.

**Quick setup (if you've already tested manually):**

1. **Copy and configure service file:**
   ```bash
   mkdir -p ~/.config/systemd/user
   cp draggg.service ~/.config/systemd/user/
   # Edit the file to set correct paths (see detailed guide above)
   ```

2. **Enable and start:**
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable draggg.service
   systemctl --user start draggg.service
   ```

3. **Check status:**
   ```bash
   systemctl --user status draggg.service
   journalctl --user -u draggg.service -f  # View logs
   ```

## How It Works: Finger Tracking and Offset Methods

### Index Finger Tracking Algorithm

draggg uses an intelligent weighted position tracking system that emphasizes the leading finger (typically the index finger) while incorporating input from all three fingers:

#### 1. **Leading Finger Identification**

The system identifies the "leading finger" based on hand orientation:
- **Right-handed users**: Leftmost finger (lowest X coordinate) - typically the index finger
- **Left-handed users**: Rightmost finger (highest X coordinate) - typically the index finger

This is determined by sorting all three finger positions by X coordinate and selecting the appropriate edge based on the `left_handed` configuration.

#### 2. **Weighted Position Calculation**

The tracking position is calculated using a weighted average:

```python
weighted_x = (leading_x × leading_weight + finger2_x × other_weight + finger3_x × other_weight) / total_weight
weighted_y = (leading_y × leading_weight + finger2_y × other_weight + finger3_y × other_weight) / total_weight
```

**Default weights:**
- Leading finger (index finger): **1.5** (50% more influence)
- Other two fingers: **0.3** each (30% combined influence)

This weighting scheme provides:
- **Smooth tracking**: The leading finger dominates, reducing jitter from fingers moving at slightly different rates
- **Natural feel**: Mimics single-finger cursor movement while maintaining three-finger gesture recognition
- **Stability**: Other fingers provide stabilizing input without overwhelming the primary tracking finger

#### 3. **Offset Calculation Method**

Once dragging begins, the system uses an offset-based approach to translate finger movement to cursor movement:

**Step 1: Initial Position Lock**
- When three fingers are detected, the system records:
  - Current cursor position (`cursor_lock_position`)
  - Initial weighted finger position (`initial_left_finger_position`)

**Step 2: Movement Offset Calculation**
For each frame during dragging:
```python
offset_x = current_finger_x - initial_finger_x
offset_y = current_finger_y - initial_finger_y
```

**Step 3: Cursor Position Update**
The offset is applied to the locked cursor position with sensitivity scaling:
```python
new_cursor_x = cursor_lock_position_x + (offset_x × drag_sensitivity)
new_cursor_y = cursor_lock_position_y + (offset_y × drag_sensitivity)
```

**Step 4: Relative Movement Emission**
The system calculates relative movement from the last position and emits it via uinput:
```python
dx = new_cursor_x - last_cursor_x
dy = new_cursor_y - last_cursor_y
```

This dual-mode approach ensures:
- **Absolute positioning**: When cursor position is available (via xdotool/X11), provides precise control
- **Relative fallback**: When cursor position is unavailable, uses pure relative movement for compatibility

#### 4. **State Machine Flow**

The gesture recognition follows this state progression:

1. **IDLE**: No gesture active
2. **THREE_FINGER_DETECTED**: Three fingers detected, starting 50ms detection delay
3. **LOCKING_POSITIONS**: Delay elapsed, locking cursor and finger positions
4. **WAITING_FOR_THRESHOLD**: Waiting for movement to exceed threshold (default: 10 pixels)
5. **DRAGGING**: Actively dragging, tracking finger movement and updating cursor
6. **RELEASING**: Fingers lifted, waiting 30ms before releasing mouse button
7. **IDLE**: Back to idle state

#### 5. **Micro-Delays for Stability**

The system includes small delays to prevent accidental activations:
- **Detection delay (50ms)**: Prevents activation from brief three-finger touches
- **Click delay (20ms)**: Small delay before mouse button press for stability
- **Release delay (30ms)**: Prevents premature release during finger adjustments

### Why This Approach Works

1. **Leading Finger Emphasis**: By giving the index finger (leading finger) more weight, the system tracks the finger that users naturally use to guide movement, resulting in intuitive control.

2. **Offset-Based Movement**: Using offsets from an initial position rather than absolute positions prevents cursor jumps and provides smooth, predictable movement.

3. **Sensitivity Scaling**: The `drag_sensitivity` parameter (default 0.25) allows fine-tuning of movement responsiveness, making it adaptable to different touchpad sizes and user preferences.

4. **Weighted Averaging**: Incorporating all three fingers while emphasizing the leading finger provides stability without sacrificing responsiveness.

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
   sudo python3 draggg.py
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
   python3 draggg.py --verbose
   ```

3. **Verify touchpad detection:**
   - Check that the correct device is being used
   - Verify three fingers are detected (check logs)

4. **Adjust sensitivity:**
   ```bash
   python3 draggg.py --drag-sensitivity 0.5
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

**Default:** 10 pixels

### Drag Sensitivity

The `drag_sensitivity` multiplier affects how cursor movement relates to finger movement. Higher values = more cursor movement per finger movement.

**Recommended:** 0.1-1.0 (lower values provide finer control)

**Default:** 0.25

### Finger Weights

- **leading_finger_weight**: Weight for the leading finger (leftmost for right-handed, rightmost for left-handed)
- **other_fingers_weight**: Weight for each of the other two fingers

These affect how finger positions are averaged. Higher leading weight makes the leading finger more influential.

**Recommended:** 
- `leading_finger_weight`: 1.0-2.0
- `other_fingers_weight`: 0.2-0.5

**Defaults:**
- `leading_finger_weight`: 1.5
- `other_fingers_weight`: 0.3

### Left-Handed Mode

Enable `left_handed` mode to use the rightmost finger (instead of leftmost) as the leading finger. This is useful for left-handed users who naturally guide with their right index finger.

## Technical Details

### Architecture

- **Input**: Reads from `/dev/input/eventX` (touchpad device) via evdev
- **Output**: Writes to `/dev/uinput` (virtual mouse device)
- **Cursor Position**: Uses xdotool or X11 API for absolute positioning (falls back to relative movement)

### Dependencies

- **python3-evdev**: Linux input event device access
- **python3-uinput**: Virtual input device creation
- **xdotool**: Cursor position queries (optional, X11 API fallback available)
- **python3-xlib**: Alternative cursor position API (optional fallback)

### Event Processing

The system processes touchpad events in frames:
1. **Event Buffering**: Individual ABS events (position, tracking ID, slot) are buffered
2. **Frame Completion**: On SYN_REPORT event, a complete frame is processed
3. **State Machine**: Frame processing updates the gesture state machine
4. **Movement Calculation**: Offset-based movement is calculated and emitted

This frame-based approach ensures synchronized processing of all three finger positions.

## Contributing

Contributions welcome! Areas for improvement:
- Additional touchpad driver support
- Wayland improvements
- Gesture customization
- Performance optimizations
- Additional gesture types

## License

[Add your license here]

## Acknowledgments

Built with:
- [python-evdev](https://github.com/gvalkov/python-evdev) - Linux input event handling
- [python-uinput](https://github.com/tuomasjjrasanen/python-uinput) - Virtual input device support
