# Three-Finger-Drag (Linux, ...)

![draggg Banner](https://raw.githubusercontent.com/j031nich0145/draggg/main/assets/dragggB3.png)

[![PyPI version](https://img.shields.io/pypi/v/draggg.svg?label=PyPI)](https://pypi.org/project/draggg/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

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
- **Python 3.9+**: Python 3.9 or higher required
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

## Installation

### Quick Install from Package Managers

**pip (Python Package Index) - Recommended:**
```bash
# One-line install - completely silent!
pip install draggg

# After installation, desktop notifications will appear asking:
#   1. Would you like to add draggg to PATH? (Yes/No)
#   2. Would you like to open GUI to configure settings? (Yes/No)

# Or install from source (latest version)
pip install git+https://github.com/j031nich0145/draggg.git

# If notifications didn't appear or you want to configure manually:
draggg-setup  # Interactive setup script
draggg-gui    # GUI configuration tool
```

**snap (Snap Store):**
```bash
# Install from Snap Store
sudo snap install draggg

# Grant necessary permissions
sudo snap connect draggg:hardware-observer
sudo snap connect draggg:x11

# Run setup
snap run draggg-gui
```

**apt (Debian/Ubuntu) - once published:**
```bash
# Add repository (instructions will be provided when published)
# sudo add-apt-repository ppa:draggg/stable
sudo apt update
sudo apt install draggg

# Or install from .deb file:
# wget https://github.com/j031nich0145/draggg/releases/latest/download/draggg.deb
# sudo apt install ./draggg.deb

# After installation:
draggg-gui
```

**conda:**
```bash
# Install from conda-forge (when available)
conda install -c conda-forge draggg

# Or build from source:
conda build conda/
conda install --use-local draggg

# After installation:
draggg-gui
```

> **Note:** After installing from pip, desktop notifications will appear asking about:
> 1. Adding draggg commands to PATH (recommended)
> 2. Opening the GUI to configure settings
> 
> The installation is completely silent - just run `pip install draggg` and wait for notifications!
> 
> If notifications didn't appear or you want to configure manually:
> - Run `draggg-setup` for interactive setup
> - Run `draggg-gui` to open the GUI configuration tool
> - Configure permissions (udev rules and input group)
> - Optionally set up the systemd service for background operation

### From Source

Clone or download this repository and run the setup script (see Quick Start below).

## Quick Start

### Option 1: GUI Setup (Recommended - Easiest)

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
   - Install desktop entry for GUI (optional)

3. **Launch the GUI:**
   - **From application menu:** Search for "draggg" in your application menu and click it
   - **From command line:**
     ```bash
     python3 draggg_gui.py
     ```

   The GUI will guide you through:
   - First-time setup (if needed)
   - Wayland to X11 switching (if necessary)
   - Dependency installation
   - Permission configuration
   - Hardware detection
   - Settings configuration
   - Service management

4. **Run draggg:**
   - The GUI can start/stop the service
   - Or run manually: `python3 draggg.py`
   - Or use the installed systemd service (starts automatically if enabled)

### Option 2: Command-Line Setup

1. **Run the interactive setup script:**
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

2. **Run the application:**
   ```bash
   # If installed as service, it should already be running
   # Otherwise, run manually:
   sudo python3 draggg.py
   # Or if permissions are configured:
   python3 draggg.py
   ```

### Option 3: Manual Build and Setup

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

**Service won't start / "bad unit file setting" error:**
1. Check for invalid directives in service file:
   ```bash
   cat ~/.config/systemd/user/draggg.service | grep -i user
   # Should be empty - User= directive is invalid for user services
   ```
2. If found, fix it:
   ```bash
   # Remove invalid User= line
   sed -i '/^User=/d' ~/.config/systemd/user/draggg.service
   systemctl --user daemon-reload
   systemctl --user start draggg.service
   ```
3. Or reinstall via GUI setup wizard (it now handles this automatically)

**Service won't start - other issues:**
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

**Icons not appearing in application menu:**
1. Verify icons installed:
   ```bash
   ls -la ~/.local/share/icons/hicolor/*/apps/draggg.png
   # Should show multiple sizes: 16x16, 22x22, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256
   ```
2. If missing, run fix script:
   ```bash
   cd draggg
   ./fix_icons.sh
   ```
3. Or reinstall via GUI setup wizard and check "Create application menu entry"
4. Update icon cache:
   ```bash
   gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
   update-desktop-database ~/.local/share/applications
   ```
5. You may need to log out/in or restart desktop environment

**Uninstalling for package manager testing:**
If you want to test installation from pip/apt/snap after installing from source:

1. **Use GUI Uninstall (easiest):**
   ```bash
   python3 draggg_gui.py
   # Go to About tab → Click "Uninstall draggg"
   # Choose what to remove (service, shortcuts, icons, config)
   ```

2. **Manual uninstall:**
   ```bash
   # Stop and remove service
   systemctl --user stop draggg.service
   systemctl --user disable draggg.service
   rm ~/.config/systemd/user/draggg.service
   systemctl --user daemon-reload
   
   # Remove desktop entry and shortcuts
   rm ~/.local/share/applications/draggg.desktop
   rm ~/Desktop/draggg.desktop 2>/dev/null
   
   # Remove icons (optional)
   rm -rf ~/.local/share/icons/hicolor/*/apps/draggg.png
   gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
   
   # Remove config (optional - keeps your settings)
   # rm ~/.config/three-finger-drag/config.json
   
   # For pip uninstall:
   pip uninstall draggg
   
   # For snap uninstall:
   sudo snap remove draggg
   
   # For apt uninstall:
   sudo apt remove draggg
   ```

3. **Then reinstall from package manager:**
   ```bash
   # pip
   pip install draggg
   draggg-gui  # Run setup wizard
   
   # snap
   sudo snap install draggg
   sudo snap connect draggg:hardware-observer
   sudo snap connect draggg:x11
   snap run draggg-gui
   
   # apt
   sudo apt install draggg
   draggg-gui
   ```

## Usage

### GUI Usage (Recommended)

**First-time setup or configuration:**
- Launch `draggg_gui.py` or click "draggg" in your application menu
- Follow the setup wizard (first time only)
- Use the settings panel to modify configuration anytime

**Managing the service:**
- Open the GUI → "Service" tab
- Start/stop the service
- Enable/disable auto-start on login
- View logs

**Changing settings:**
- Open the GUI → Modify settings in "General" or "Advanced" tabs
- Click "Save Settings"

### Command-Line Usage

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

### ⚠️ IMPORTANT: pip Install Loop Fix (Version 1.0.10 Issue)

**If `pip install draggg` gets stuck in a loop** trying to install evdev (you see repeated "metadata for project name unknown" errors), **this is a known issue with version 1.0.10**. 

**Quick Fix (Choose One):**

1. **Install evdev constraint first** (fastest):
   ```bash
   pip install "evdev>=1.4.0,<1.7.0"
   pip install draggg
   ```

2. **Use system packages** (recommended):
   ```bash
   sudo apt install python3-evdev python3-uinput  # Ubuntu/Debian
   sudo dnf install python3-evdev python3-uinput    # Fedora
   sudo pacman -S python-evdev python-uinput       # Arch
   pip install draggg
   ```

3. **Install from GitHub** (latest version with fix):
   ```bash
   pip install git+https://github.com/j031nich0145/draggg.git
   ```

**Note:** Version 1.0.12+ includes a fix that pins evdev to `<1.7.0` to avoid this issue. The workarounds above are for users installing version 1.0.10 or earlier.

### pip Install Issues - evdev Dependency Loop (Detailed)

If `pip install draggg` gets stuck in a loop trying to install evdev (you see repeated "metadata for project name unknown" errors), this is due to broken metadata in evdev versions 1.7.0+ on PyPI.

**Note:** Version 1.0.12+ includes a fix that pins evdev to `<1.7.0` to avoid this issue. If you're installing version 1.0.10 or earlier, or if you still encounter issues with 1.0.12+, use the workarounds below.

**Solution 1: Install System Packages First (Recommended)**
```bash
# Install system packages BEFORE pip install
sudo apt install python3-evdev python3-uinput xdotool python3-xlib  # Ubuntu/Debian
sudo dnf install python3-evdev python3-uinput xdotool python3-xlib  # Fedora
sudo pacman -S python-evdev python-uinput xdotool python-xlib  # Arch

# Then install draggg (it will skip evdev/python-uinput if already installed)
pip install draggg
```

**Solution 2: Use Version Constraint**
If you must install via pip and are using version 1.0.10 or earlier, or if you encounter issues with 1.0.12+, manually install evdev with the version constraint first:
```bash
# Install evdev from an older version manually first
pip install "evdev>=1.4.0,<1.7.0"
pip install draggg
```

**Solution 3: Use Alternative Installation Methods**
- Use **snap**: `sudo snap install draggg` (includes all dependencies)
- Install from **source**: Clone repo and use system packages
- Use **conda**: `conda install -c conda-forge draggg` (when available)

**Why System Packages Are Preferred:**
- System packages (`python3-evdev`) are pre-compiled and don't require kernel headers
- They're better maintained and integrated with your distribution
- Avoid PyPI metadata issues entirely
- Better security through distribution package management

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

**Automated Wayland to X11 Conversion:**

draggg includes a helper tool to automatically convert Wayland sessions to X11:

```bash
# Launch the TUI helper (recommended)
draggg --wayland-helper

# Or use the standalone commands
wayland-to-x11-tui    # Interactive TUI helper
wayland-to-x11        # Command-line conversion script
```

The helper will:
- Detect your display manager (GDM, LightDM, SDDM)
- Backup your current configuration
- Modify the display manager config to disable Wayland
- Offer to log out immediately

**Supported Display Managers:**
- GDM (Ubuntu/Debian, Fedora) - Fully supported
- LightDM, SDDM - Detection supported, manual configuration required

**Manual Conversion:**

If automatic conversion doesn't work, you can manually edit the GDM config:

1. **Ubuntu/Debian**: Edit `/etc/gdm3/custom.conf`
2. **Fedora**: Edit `/etc/gdm/custom.conf`
3. Find the `[daemon]` section
4. Uncomment or add: `WaylandEnable=false`
5. Log out and log back in

### Commands Not Found After Installation

If `draggg` or `draggg-gui` commands are not found after `pip install draggg`:

**Automatic Setup (Recommended):**

The post-installation setup script should run automatically after `pip install draggg`. If it didn't run or you skipped PATH configuration:

```bash
# Run the interactive setup script
draggg-setup
```

This will:
- Detect your shell and add `~/.local/bin` to PATH
- Offer Wayland to X11 conversion (if needed)
- Install desktop entry and icons
- Update icon cache and desktop database

**Manual PATH Configuration:**

If you prefer to configure PATH manually:

1. **Check where scripts are installed:**
   ```bash
   python3 -m site --user-base
   # Output example: /home/username/.local
   # Scripts are in: /home/username/.local/bin
   ```

2. **Check if scripts directory is in PATH:**
   ```bash
   echo $PATH | grep -q "$HOME/.local/bin" && echo "OK - in PATH" || echo "NOT in PATH"
   ```

3. **Add to PATH if needed:**
   
   **For bash (most Linux systems):**
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
   
   **For zsh:**
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```
   
   **For fish:**
   ```bash
   fish_add_path ~/.local/bin
   ```

4. **Verify commands work:**
   ```bash
   which draggg
   which draggg-gui
   draggg --help
   ```

5. **Alternative: Use full path temporarily:**
   ```bash
   ~/.local/bin/draggg --help
   ~/.local/bin/draggg-gui
   ```

**Note:** After adding to PATH, you may need to:
- Open a new terminal window, or
- Run `source ~/.bashrc` (or equivalent for your shell)

### Desktop File Icon Not Displaying

If the draggg icon doesn't appear in your application menu:

1. **Update icon cache:**
   ```bash
   gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor
   ```

2. **Update desktop database:**
   ```bash
   update-desktop-database ~/.local/share/applications
   ```

3. **Log out and back in** (or restart your desktop environment)

4. **Verify icon files exist:**
   ```bash
   ls -la ~/.local/share/icons/hicolor/*/apps/draggg.png
   ```

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

## Packaging and Distribution

### Building Packages

**Python Package (pip):**
```bash
python3 setup.py sdist bdist_wheel
pip install dist/draggg-*.whl
```

**Snap Package:**
```bash
snapcraft
sudo snap install draggg_*.snap --dangerous
```

**Debian Package:**
```bash
dpkg-buildpackage -b
sudo dpkg -i ../draggg_*.deb
```

**Conda Package:**
```bash
conda build conda/
conda install --use-local draggg
```

### Creating Shortcuts

When installing from source using `setup.sh`, you'll be prompted to create shortcuts:
- **Application Menu Entry**: Adds draggg to your application menu
- **Desktop Shortcut**: Creates a shortcut on your desktop

You can also create shortcuts later using the GUI setup wizard or manually copying the desktop file.

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
- **Multi-platform support** - macOS and Windows (see [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md))

For detailed contributor guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

For information about planned macOS and Windows support, see [FUTURE_PLATFORMS.md](FUTURE_PLATFORMS.md).

## License

[Add your license here]

## Acknowledgments

Built with:
- [python-evdev](https://github.com/gvalkov/python-evdev) - Linux input event handling
- [python-uinput](https://github.com/tuomasjjrasanen/python-uinput) - Virtual input device support
