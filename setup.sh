#!/bin/bash
#
# draggg - Linux Three-Finger Drag - Interactive Setup Script
# Handles installation, configuration, and service setup
# Comprehensive and adaptable for various Linux distributions
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local answer
    
    while true; do
        if [ "$default" = "y" ]; then
            read -p "$prompt [Y/n]: " answer
            answer="${answer:-y}"
        else
            read -p "$prompt [y/N]: " answer
            answer="${answer:-n}"
        fi
        
        case "$answer" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/redhat-release ]; then
        echo "fedora"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    else
        echo "unknown"
    fi
}

check_command() {
    command -v "$1" >/dev/null 2>&1
}

check_python_package() {
    python3 -c "import $1" 2>/dev/null
}

check_pip() {
    command -v pip3 >/dev/null 2>&1 || python3 -m pip --version >/dev/null 2>&1
}

get_pip_command() {
    if command -v pip3 >/dev/null 2>&1; then
        echo "pip3"
    elif python3 -m pip --version >/dev/null 2>&1; then
        echo "python3 -m pip"
    else
        echo ""
    fi
}

parse_requirements_txt() {
    local req_file="$1"
    local packages=()
    
    if [ ! -f "$req_file" ]; then
        return 1
    fi
    
    # Read requirements.txt and extract package names (skip comments and empty lines)
    while IFS= read -r line || [ -n "$line" ]; do
        # Remove leading/trailing whitespace (portable method)
        line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Skip empty lines and comments
        if [ -z "$line" ] || [[ "$line" =~ ^# ]]; then
            continue
        fi
        
        # Extract package name (before any version specifiers, comments, or spaces)
        # Handle formats like: "package>=1.0", "package==1.0", "package", "package # comment"
        local pkg=$(echo "$line" | sed 's/[<>=!].*//' | sed 's/#.*//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Skip if it's a system package note or empty
        if [ -n "$pkg" ] && [[ ! "$pkg" =~ ^(python3-|xdotool|python-xlib) ]]; then
            packages+=("$pkg")
        fi
    done < "$req_file"
    
    # Output packages (one per line) for processing
    printf '%s\n' "${packages[@]}"
}

check_pip_packages() {
    local req_file="$SCRIPT_DIR/requirements.txt"
    local missing=()
    local optional_packages=("pystray" "Pillow")  # Optional packages (for tray icon)
    
    if [ ! -f "$req_file" ]; then
        return 0  # No requirements.txt, nothing to check
    fi
    
    local packages
    packages=$(parse_requirements_txt "$req_file")
    
    if [ -z "$packages" ]; then
        return 0  # No packages found
    fi
    
    while IFS= read -r pkg; do
        [ -z "$pkg" ] && continue
        
        # Skip optional packages (they're nice to have but not required)
        local is_optional=0
        for opt_pkg in "${optional_packages[@]}"; do
            if [ "$pkg" = "$opt_pkg" ]; then
                is_optional=1
                break
            fi
        done
        if [ $is_optional -eq 1 ]; then
            continue  # Skip optional packages
        fi
        
        # Check if package is importable
        # Map package names to import names
        local import_name="$pkg"
        case "$pkg" in
            python-uinput)
                import_name="uinput"
                ;;
            evdev)
                import_name="evdev"
                ;;
        esac
        
        if ! check_python_package "$import_name"; then
            missing+=("$pkg")
        fi
    done <<< "$packages"
    
    if [ ${#missing[@]} -gt 0 ]; then
        printf '%s\n' "${missing[@]}"
        return 1
    fi
    
    return 0
}

install_pip_packages() {
    local missing_packages="$1"
    local pip_cmd
    
    pip_cmd=$(get_pip_command)
    
    if [ -z "$pip_cmd" ]; then
        print_error "pip3 not found. Cannot install Python packages."
        print_info "Install pip3 with: sudo apt install python3-pip  # Ubuntu/Debian"
        print_info "                   sudo dnf install python3-pip  # Fedora"
        print_info "                   sudo pacman -S python-pip     # Arch"
        return 1
    fi
    
    print_info "Installing missing Python packages via pip..."
    
    local packages_to_install=()
    while IFS= read -r pkg; do
        [ -z "$pkg" ] && continue
        packages_to_install+=("$pkg")
    done <<< "$missing_packages"
    
    if [ ${#packages_to_install[@]} -eq 0 ]; then
        return 0
    fi
    
    print_info "Packages to install: ${packages_to_install[*]}"
    
    if prompt_yes_no "Install missing Python packages via pip?" "y"; then
        # Install packages
        # Handle both "pip3" and "python3 -m pip" formats
        if [ "$pip_cmd" = "pip3" ]; then
            if pip3 install --user "${packages_to_install[@]}"; then
                print_success "Python packages installed successfully"
                return 0
            else
                print_warning "Some packages failed to install via pip"
                print_info "You may need to install system packages instead"
                return 1
            fi
        elif [ "$pip_cmd" = "python3 -m pip" ]; then
            if python3 -m pip install --user "${packages_to_install[@]}"; then
                print_success "Python packages installed successfully"
                return 0
            else
                print_warning "Some packages failed to install via pip"
                print_info "You may need to install system packages instead"
                return 1
            fi
        else
            print_error "Invalid pip command: $pip_cmd"
            return 1
        fi
    else
        print_info "Skipping pip package installation"
        return 1
    fi
}

install_dependencies_debian() {
    print_info "Installing dependencies for Debian/Ubuntu..."
    sudo apt update
    sudo apt install -y python3-evdev python3-uinput xdotool python3-xlib
}

install_dependencies_fedora() {
    print_info "Installing dependencies for Fedora..."
    sudo dnf install -y python3-evdev python3-uinput xdotool python3-xlib
}

install_dependencies_arch() {
    print_info "Installing dependencies for Arch Linux..."
    sudo pacman -S --noconfirm python-evdev python-uinput xdotool python-xlib
}

check_dependencies() {
    local missing_system=()
    local missing_pip=""
    
    # Check system packages
    if ! check_python_package "evdev"; then
        missing_system+=("python3-evdev")
    fi
    
    if ! check_python_package "uinput"; then
        missing_system+=("python3-uinput")
    fi
    
    if ! check_command "xdotool"; then
        missing_system+=("xdotool")
    fi
    
    # Check pip packages from requirements.txt
    missing_pip=$(check_pip_packages)
    local pip_check_result=$?
    
    # Report missing dependencies
    if [ ${#missing_system[@]} -gt 0 ]; then
        print_warning "Missing system dependencies: ${missing_system[*]}"
    fi
    
    if [ $pip_check_result -ne 0 ] && [ -n "$missing_pip" ]; then
        local pip_packages
        pip_packages=$(echo "$missing_pip" | tr '\n' ' ')
        print_warning "Missing Python packages (from requirements.txt): $pip_packages"
    fi
    
    # Note: pystray and Pillow are optional (for system tray icon feature)
    if ! check_python_package "pystray"; then
        print_info "Note: pystray is optional (only needed for system tray icon)"
    fi
    
    if [ ${#missing_system[@]} -gt 0 ] || [ $pip_check_result -ne 0 ]; then
        return 1
    fi
    
    return 0
}

install_dependencies() {
    local distro=$(detect_distro)
    
    case "$distro" in
        ubuntu|debian)
            install_dependencies_debian
            ;;
        fedora)
            install_dependencies_fedora
            ;;
        arch)
            install_dependencies_arch
            ;;
        *)
            print_error "Unsupported distribution: $distro"
            print_info "Please install dependencies manually:"
            print_info "  - python3-evdev"
            print_info "  - python3-uinput"
            print_info "  - xdotool"
            print_info "  - python3-xlib (optional)"
            return 1
            ;;
    esac
}

setup_udev_rules() {
    print_info "Setting up udev rules for uinput access..."
    
    local udev_rule="/etc/udev/rules.d/99-uinput.rules"
    
    if [ -f "$udev_rule" ]; then
        print_warning "Udev rule already exists: $udev_rule"
        if ! prompt_yes_no "Overwrite existing rule?" "n"; then
            return 0
        fi
    fi
    
    echo 'KERNEL=="uinput", MODE="0666"' | sudo tee "$udev_rule" > /dev/null
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    print_success "Udev rules configured"
}

setup_user_group() {
    print_info "Checking user group membership..."
    
    if groups | grep -q "\binput\b"; then
        print_success "User is already in 'input' group"
        return 0
    fi
    
    print_warning "User is not in 'input' group"
    if prompt_yes_no "Add user to 'input' group? (requires logout/login)" "y"; then
        sudo usermod -a -G input "$USER"
        print_success "User added to 'input' group"
        print_warning "Please log out and back in for changes to take effect"
    else
        print_info "You can run the application with sudo instead"
    fi
}

detect_touchpad() {
    print_info "Detecting touchpad hardware..."
    echo
    print_info "This will scan your system for compatible multi-touch touchpads."
    echo
    
    if [ -f "$SCRIPT_DIR/detect_hardware.py" ]; then
        python3 "$SCRIPT_DIR/detect_hardware.py"
        echo
        
        if prompt_yes_no "Did you see a compatible touchpad listed above?" "y"; then
            echo
            print_info "You can specify a device path manually, or let draggg auto-detect."
            read -p "Enter device path (or press Enter for auto-detect): " device_path
            if [ -n "$device_path" ]; then
                print_success "Will use device: $device_path"
            else
                print_info "Will use auto-detection (recommended)"
            fi
        else
            print_warning "No compatible touchpad detected."
            echo
            print_info "Troubleshooting steps:"
            echo "  1. Make sure you have a multi-touch trackpad"
            echo "  2. Check permissions: ls -l /dev/input/event*"
            echo "  3. Try running detect_hardware.py with sudo: sudo python3 detect_hardware.py"
            echo "  4. The script will attempt auto-detection when running draggg"
            echo
        fi
    else
        print_warning "detect_hardware.py not found. Skipping hardware detection."
        print_info "The script will attempt auto-detection when running draggg."
        echo ""
    fi
}

configure_settings() {
    print_header "Configuration"
    
    print_info "You can configure draggg settings now, or use defaults and adjust later."
    echo
    
    local device_path=""
    local threshold=""
    local sensitivity=""
    local left_handed="n"
    local leading_weight=""
    local other_weight=""
    
    if prompt_yes_no "Would you like to configure settings now?" "y"; then
        echo
        print_info "Device Configuration"
        echo "The script will auto-detect your touchpad, but you can specify a device path manually."
        read -p "Device path (or press Enter for auto-detect): " device_path
        
        echo
        print_info "Movement Threshold"
        echo "How far (in pixels) your fingers must move before dragging starts."
        echo "Lower values = more sensitive (recommended: 5-15, default: 10)"
        read -p "Movement threshold [10]: " threshold
        threshold="${threshold:-10}"
        
        # Validate threshold
        if ! [[ "$threshold" =~ ^[0-9]+$ ]] || [ "$threshold" -lt 1 ] || [ "$threshold" -gt 100 ]; then
            print_warning "Invalid threshold, using default: 10"
            threshold="10"
        fi
        
        echo
        print_info "Drag Sensitivity"
        echo "How much the cursor moves relative to finger movement."
        echo "Lower values = finer control (recommended: 0.1-1.0, default: 0.25)"
        read -p "Drag sensitivity [0.25]: " sensitivity
        sensitivity="${sensitivity:-0.25}"
        
        # Validate sensitivity (basic check)
        if ! [[ "$sensitivity" =~ ^[0-9]+\.?[0-9]*$ ]] || (( $(echo "$sensitivity <= 0" | bc -l) )) || (( $(echo "$sensitivity > 5" | bc -l) )); then
            print_warning "Invalid sensitivity, using default: 0.25"
            sensitivity="0.25"
        fi
        
        echo
        print_info "Left-Handed Mode"
        echo "Left-handed mode uses the rightmost finger (instead of leftmost) as the leading finger."
        if prompt_yes_no "Enable left-handed mode?" "n"; then
            left_handed="y"
        fi
        
        echo
        print_info "Advanced: Finger Weights"
        echo "These control how finger positions are averaged. Higher leading weight = more influence from the index finger."
        echo "You can use defaults or customize for your preference."
        
        if prompt_yes_no "Customize finger weights?" "n"; then
            echo "Leading finger weight (index finger influence, recommended: 1.0-2.0, default: 1.5)"
            read -p "Leading finger weight [1.5]: " leading_weight
            leading_weight="${leading_weight:-1.5}"
            
            echo "Other fingers weight (each of the other two fingers, recommended: 0.2-0.5, default: 0.3)"
            read -p "Other fingers weight [0.3]: " other_weight
            other_weight="${other_weight:-0.3}"
        else
            leading_weight="1.5"
            other_weight="0.3"
        fi
        
        # Create config directory
        mkdir -p ~/.config/three-finger-drag
        
        # Create config file
        cat > ~/.config/three-finger-drag/config.json << EOF
{
    "device": ${device_path:+$(echo "\"$device_path\"")}${device_path:-null},
    "threshold": $threshold,
    "drag_sensitivity": $sensitivity,
    "left_handed": $([ "$left_handed" = "y" ] && echo "true" || echo "false"),
    "leading_finger_weight": $leading_weight,
    "other_fingers_weight": $other_weight
}
EOF
        
        print_success "Configuration saved to ~/.config/three-finger-drag/config.json"
        echo
        print_info "You can edit this file later or use command-line arguments to override settings."
    else
        print_info "Using default settings. You can configure later by editing ~/.config/three-finger-drag/config.json"
    fi
}

install_desktop_entry() {
    local create_app_menu="${1:-true}"
    local create_desktop_shortcut="${2:-false}"
    
    print_info "Installing desktop entry for GUI application..."
    
    local desktop_file="$SCRIPT_DIR/draggg.desktop"
    
    if [ ! -f "$desktop_file" ]; then
        print_warning "Desktop file not found: $desktop_file"
        return 1
    fi
    
    # Install to application menu
    if [ "$create_app_menu" = "true" ]; then
        local target_dir="$HOME/.local/share/applications"
        local target_file="$target_dir/draggg.desktop"
        
        mkdir -p "$target_dir"
        
        # Update paths in desktop file - handle both /path/to/draggg placeholder and actual paths
        sed "s|/path/to/draggg|$SCRIPT_DIR|g" "$desktop_file" > "$target_file"
        
        # Also update Exec line to use absolute path
        python3_path=$(which python3)
        if [ -n "$python3_path" ]; then
            sed -i "s|Exec=python3 |Exec=$python3_path |g" "$target_file"
        fi
        
        # Install icon to icon theme directory and update desktop entry
        if [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
            # Install icons to user icon theme directory - all sizes for proper display
            mkdir -p "$HOME/.local/share/icons/hicolor/256x256/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/128x128/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/64x64/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/48x48/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/32x32/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/24x24/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/22x22/apps"
            mkdir -p "$HOME/.local/share/icons/hicolor/16x16/apps"
            
            # Copy existing icons
            cp "$SCRIPT_DIR/assets/icon.png" "$HOME/.local/share/icons/hicolor/256x256/apps/draggg.png" 2>/dev/null || true
            [ -f "$SCRIPT_DIR/assets/icon-128.png" ] && cp "$SCRIPT_DIR/assets/icon-128.png" "$HOME/.local/share/icons/hicolor/128x128/apps/draggg.png" 2>/dev/null || true
            [ -f "$SCRIPT_DIR/assets/icon-64.png" ] && cp "$SCRIPT_DIR/assets/icon-64.png" "$HOME/.local/share/icons/hicolor/64x64/apps/draggg.png" 2>/dev/null || true
            [ -f "$SCRIPT_DIR/assets/icon-48.png" ] && cp "$SCRIPT_DIR/assets/icon-48.png" "$HOME/.local/share/icons/hicolor/48x48/apps/draggg.png" 2>/dev/null || true
            
            # Use 48x48 for smaller sizes if available, otherwise use 64x64 or largest available
            if [ -f "$SCRIPT_DIR/assets/icon-48.png" ]; then
                cp "$SCRIPT_DIR/assets/icon-48.png" "$HOME/.local/share/icons/hicolor/32x32/apps/draggg.png" 2>/dev/null || true
                cp "$SCRIPT_DIR/assets/icon-48.png" "$HOME/.local/share/icons/hicolor/24x24/apps/draggg.png" 2>/dev/null || true
                cp "$SCRIPT_DIR/assets/icon-48.png" "$HOME/.local/share/icons/hicolor/22x22/apps/draggg.png" 2>/dev/null || true
                cp "$SCRIPT_DIR/assets/icon-48.png" "$HOME/.local/share/icons/hicolor/16x16/apps/draggg.png" 2>/dev/null || true
            elif [ -f "$SCRIPT_DIR/assets/icon-64.png" ]; then
                cp "$SCRIPT_DIR/assets/icon-64.png" "$HOME/.local/share/icons/hicolor/32x32/apps/draggg.png" 2>/dev/null || true
                cp "$SCRIPT_DIR/assets/icon-64.png" "$HOME/.local/share/icons/hicolor/24x24/apps/draggg.png" 2>/dev/null || true
                cp "$SCRIPT_DIR/assets/icon-64.png" "$HOME/.local/share/icons/hicolor/22x22/apps/draggg.png" 2>/dev/null || true
                cp "$SCRIPT_DIR/assets/icon-64.png" "$HOME/.local/share/icons/hicolor/16x16/apps/draggg.png" 2>/dev/null || true
            fi
            
            # Update desktop entry to use icon name (not path)
            sed -i "s|Icon=.*|Icon=draggg|g" "$target_file"
            
            # Update icon cache if available (use -f flag to force, -t to ignore timestamps)
            if command -v gtk-update-icon-cache >/dev/null 2>&1; then
                gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
            fi
        fi
        
        # Update Path if present
        sed -i "s|^Path=.*|Path=$SCRIPT_DIR|g" "$target_file"
        
        chmod +x "$target_file"
        
        # Update desktop database if command exists
        if command -v update-desktop-database >/dev/null 2>&1; then
            update-desktop-database "$target_dir" 2>/dev/null || true
        fi
        
        print_success "Application menu entry installed at $target_file"
        print_info "You can now find 'draggg' in your application menu"
    fi
    
    # Install desktop shortcut
    if [ "$create_desktop_shortcut" = "true" ]; then
        local desktop_dir="$HOME/Desktop"
        local desktop_shortcut="$desktop_dir/draggg.desktop"
        
        # Check if Desktop directory exists (different names in different languages)
        if [ ! -d "$desktop_dir" ]; then
            # Try common alternative names
            for alt_dir in "$HOME/Desktop" "$HOME/桌面" "$HOME/Escritorio" "$HOME/Рабочий стол"; do
                if [ -d "$alt_dir" ]; then
                    desktop_dir="$alt_dir"
                    desktop_shortcut="$desktop_dir/draggg.desktop"
                    break
                fi
            done
        fi
        
        if [ -d "$desktop_dir" ]; then
            # Copy and update desktop file for shortcut
            sed "s|/path/to/draggg|$SCRIPT_DIR|g" "$desktop_file" > "$desktop_shortcut"
            
            python3_path=$(which python3)
            if [ -n "$python3_path" ]; then
                sed -i "s|Exec=python3 |Exec=$python3_path |g" "$desktop_shortcut"
            fi
            
            # Icon will be referenced by name from icon theme (already installed above if app menu was created)
            # For desktop shortcut, we can use absolute path as fallback
            if [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
                # Try icon theme name first, fallback to absolute path
                sed -i "s|Icon=.*|Icon=draggg|g" "$desktop_shortcut"
            fi
            
            sed -i "s|^Path=.*|Path=$SCRIPT_DIR|g" "$desktop_shortcut"
            
            chmod +x "$desktop_shortcut"
            
            print_success "Desktop shortcut created at $desktop_shortcut"
        else
            print_warning "Desktop directory not found. Skipping desktop shortcut creation."
        fi
    fi
}

install_service() {
    print_header "Systemd Service Installation"
    
    if ! prompt_yes_no "Install as systemd user service (runs in background)?" "y"; then
        return 0
    fi
    
    local service_dir="$HOME/.config/systemd/user"
    local service_file="$service_dir/draggg.service"
    
    mkdir -p "$service_dir"
    
    # Determine script name
    local script_name="draggg.py"
    if [ ! -f "$SCRIPT_DIR/draggg.py" ] && [ -f "$SCRIPT_DIR/three_finger_drag.py" ]; then
        script_name="three_finger_drag.py"
        print_warning "Using old script name. Consider renaming to draggg.py"
    fi
    
    # Create service file with correct paths
    cat > "$service_file" << EOF
[Unit]
Description=draggg - Linux Three-Finger Drag Gesture Handler
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
ExecStart=$(which python3) $SCRIPT_DIR/$script_name --config $HOME/.config/three-finger-drag/config.json --tray
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF
    
    # Reload systemd
    systemctl --user daemon-reload
    
    if prompt_yes_no "Enable and start the service now?" "y"; then
        systemctl --user enable draggg.service
        systemctl --user start draggg.service
        
        print_success "Service installed and started"
        print_info "Check status with: systemctl --user status draggg.service"
        print_info "View logs with: journalctl --user -u draggg.service -f"
    else
        print_success "Service file created at $service_file"
        print_info "Enable it later with: systemctl --user enable draggg.service"
    fi
}

verify_installation() {
    print_header "Verification"
    
    print_info "Checking installation..."
    
    local all_ok=true
    
    # Check dependencies
    if check_dependencies; then
        print_success "All dependencies installed"
    else
        print_error "Some dependencies are missing"
        all_ok=false
    fi
    
    # Check udev rules
    if [ -f "/etc/udev/rules.d/99-uinput.rules" ]; then
        print_success "Udev rules configured"
    else
        print_warning "Udev rules not configured (may need sudo to run)"
    fi
    
    # Check Python script
    if [ -f "$SCRIPT_DIR/draggg.py" ]; then
        print_success "Main script found (draggg.py)"
    elif [ -f "$SCRIPT_DIR/three_finger_drag.py" ]; then
        print_warning "Old script name found (three_finger_drag.py). Consider renaming to draggg.py"
        print_success "Main script found"
    else
        print_error "Main script not found: $SCRIPT_DIR/draggg.py"
        all_ok=false
    fi
    
    echo
    
    if [ "$all_ok" = true ]; then
        print_success "Installation verification complete!"
        echo
        print_info "To run manually:"
        if [ -f "$SCRIPT_DIR/draggg.py" ]; then
            echo "  python3 $SCRIPT_DIR/draggg.py"
        else
            echo "  python3 $SCRIPT_DIR/three_finger_drag.py"
        fi
        echo
        if [ -f ~/.config/three-finger-drag/config.json ]; then
            print_info "Or with config file:"
            if [ -f "$SCRIPT_DIR/draggg.py" ]; then
                echo "  python3 $SCRIPT_DIR/draggg.py --config ~/.config/three-finger-drag/config.json"
            else
                echo "  python3 $SCRIPT_DIR/three_finger_drag.py --config ~/.config/three-finger-drag/config.json"
            fi
        fi
    else
        print_warning "Some issues detected. Please review above messages."
    fi
}

# Main installation flow
main() {
    clear
    print_header "draggg - Linux Three-Finger Drag Setup"
    echo
    print_info "This setup script will guide you through installation and configuration."
    print_info "You can skip any step by answering 'no' or pressing Enter for defaults."
    echo
    
    # System check
    print_header "System Check"
    
    local session_type="${XDG_SESSION_TYPE:-unknown}"
    print_info "Session type: $session_type"
    
    if [ "$session_type" != "x11" ] && [ "$session_type" != "wayland" ]; then
        print_warning "Unknown session type. X11 or Wayland recommended."
    fi
    
    local distro=$(detect_distro)
    print_info "Distribution: $distro"
    echo
    
    # Dependencies
    print_header "Dependencies"
    
    if ! check_dependencies; then
        local missing_system=()
        local missing_pip=""
        
        # Re-check to get missing packages
        if ! check_python_package "evdev"; then
            missing_system+=("python3-evdev")
        fi
        if ! check_python_package "uinput"; then
            missing_system+=("python3-uinput")
        fi
        if ! check_command "xdotool"; then
            missing_system+=("xdotool")
        fi
        missing_pip=$(check_pip_packages)
        
        if prompt_yes_no "Install missing dependencies?" "y"; then
            # First try system packages (preferred)
            if [ ${#missing_system[@]} -gt 0 ]; then
                echo
                print_info "Installing system packages..."
                install_dependencies
                echo
            fi
            
            # Then try pip packages if still missing
            if [ -n "$missing_pip" ]; then
                # Re-check which packages are still missing after system install
                local still_missing_pip
                still_missing_pip=$(check_pip_packages)
                
                if [ -n "$still_missing_pip" ]; then
                    echo
                    print_info "Some packages may need to be installed via pip"
                    install_pip_packages "$still_missing_pip"
                    echo
                fi
            fi
            
            # Final check
            echo
            if ! check_dependencies; then
                print_warning "Some dependencies may still be missing"
                print_info "You can try installing manually or continue anyway"
                if ! prompt_yes_no "Continue with setup?" "y"; then
                    exit 1
                fi
            else
                print_success "All dependencies installed successfully"
            fi
        else
            print_error "Cannot continue without dependencies"
            exit 1
        fi
    else
        print_success "All dependencies already installed"
    fi
    echo
    
    # Permissions
    print_header "Permissions Setup"
    
    if prompt_yes_no "Set up udev rules for uinput access?" "y"; then
        setup_udev_rules
    fi
    echo
    
    setup_user_group
    echo
    
    # Hardware detection
    print_header "Hardware Detection"
    detect_touchpad
    echo
    
    # Configuration
    configure_settings
    echo
    
    # Desktop entry installation
    if [ -f "$SCRIPT_DIR/draggg.desktop" ]; then
        local install_app_menu="n"
        local install_desktop_shortcut="n"
        
        if prompt_yes_no "Create application shortcuts?" "y"; then
            if prompt_yes_no "Create application menu entry?" "y"; then
                install_app_menu="y"
            fi
            
            if prompt_yes_no "Create desktop shortcut?" "n"; then
                install_desktop_shortcut="y"
            fi
            
            if [ "$install_app_menu" = "y" ] || [ "$install_desktop_shortcut" = "y" ]; then
                install_desktop_entry "$install_app_menu" "$install_desktop_shortcut"
            fi
        fi
        echo
    fi
    
    # Service installation
    if systemctl --user >/dev/null 2>&1; then
        install_service
        echo
    else
        print_info "Systemd user services not available. Skipping service installation."
        echo
    fi
    
    # Verification
    verify_installation
    echo
    
    print_header "Setup Complete!"
    print_success "draggg is ready to use!"
    echo
    print_info "Next steps:"
    echo "  1. If you added yourself to the 'input' group, log out and back in"
    echo "  2. Test the gesture: Place three fingers on your trackpad and move them"
    echo "  3. Adjust settings in ~/.config/three-finger-drag/config.json if needed"
    echo "  4. Check the README.md for detailed documentation on finger tracking and configuration"
    echo
    print_info "For troubleshooting, run: python3 detect_hardware.py"
    echo
}

# Run main function
main

