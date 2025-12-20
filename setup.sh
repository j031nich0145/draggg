#!/bin/bash
#
# Linux Three-Finger Drag - Interactive Setup Script
# Handles installation, configuration, and service setup
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
    local missing=()
    
    if ! check_python_package "evdev"; then
        missing+=("python3-evdev")
    fi
    
    if ! check_python_package "uinput"; then
        missing+=("python3-uinput")
    fi
    
    if ! check_command "xdotool"; then
        missing+=("xdotool")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        print_warning "Missing dependencies: ${missing[*]}"
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
    
    if [ -f "$SCRIPT_DIR/detect_hardware.py" ]; then
        python3 "$SCRIPT_DIR/detect_hardware.py"
        echo
        
        if prompt_yes_no "Did you see a compatible touchpad listed above?" "y"; then
            read -p "Enter device path (or press Enter for auto-detect): " device_path
            echo "$device_path"
        else
            print_warning "No compatible touchpad detected. You may need to troubleshoot."
            echo ""
        fi
    else
        print_warning "detect_hardware.py not found. Skipping hardware detection."
        echo ""
    fi
}

configure_settings() {
    print_header "Configuration"
    
    local device_path=""
    local threshold=""
    local sensitivity=""
    local left_handed="n"
    
    if prompt_yes_no "Would you like to configure settings now?" "y"; then
        read -p "Device path (or Enter for auto-detect): " device_path
        
        read -p "Movement threshold [10]: " threshold
        threshold="${threshold:-10}"
        
        read -p "Drag sensitivity [1.0]: " sensitivity
        sensitivity="${sensitivity:-1.0}"
        
        if prompt_yes_no "Left-handed mode?" "n"; then
            left_handed="y"
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
    "leading_finger_weight": 1.5,
    "other_fingers_weight": 0.3
}
EOF
        
        print_success "Configuration saved to ~/.config/three-finger-drag/config.json"
    fi
}

install_service() {
    print_header "Systemd Service Installation"
    
    if ! prompt_yes_no "Install as systemd user service (runs in background)?" "y"; then
        return 0
    fi
    
    local service_dir="$HOME/.config/systemd/user"
    local service_file="$service_dir/three-finger-drag.service"
    
    mkdir -p "$service_dir"
    
    # Create service file with correct paths
    cat > "$service_file" << EOF
[Unit]
Description=Linux Three-Finger Drag Gesture Handler
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
ExecStart=$(which python3) $SCRIPT_DIR/three_finger_drag.py --config $HOME/.config/three-finger-drag/config.json
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF
    
    # Reload systemd
    systemctl --user daemon-reload
    
    if prompt_yes_no "Enable and start the service now?" "y"; then
        systemctl --user enable three-finger-drag.service
        systemctl --user start three-finger-drag.service
        
        print_success "Service installed and started"
        print_info "Check status with: systemctl --user status three-finger-drag.service"
        print_info "View logs with: journalctl --user -u three-finger-drag.service -f"
    else
        print_success "Service file created at $service_file"
        print_info "Enable it later with: systemctl --user enable three-finger-drag.service"
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
    if [ -f "$SCRIPT_DIR/three_finger_drag.py" ]; then
        print_success "Main script found"
    else
        print_error "Main script not found: $SCRIPT_DIR/three_finger_drag.py"
        all_ok=false
    fi
    
    echo
    
    if [ "$all_ok" = true ]; then
        print_success "Installation verification complete!"
        echo
        print_info "To run manually:"
        echo "  python3 $SCRIPT_DIR/three_finger_drag.py"
        echo
        if [ -f ~/.config/three-finger-drag/config.json ]; then
            print_info "Or with config file:"
            echo "  python3 $SCRIPT_DIR/three_finger_drag.py --config ~/.config/three-finger-drag/config.json"
        fi
    else
        print_warning "Some issues detected. Please review above messages."
    fi
}

# Main installation flow
main() {
    clear
    print_header "Linux Three-Finger Drag - Setup"
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
        if prompt_yes_no "Install missing dependencies?" "y"; then
            install_dependencies
            echo
            
            # Re-check after installation
            if ! check_dependencies; then
                print_error "Some dependencies failed to install"
                exit 1
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
    print_success "Linux Three-Finger Drag is ready to use"
    echo
}

# Run main function
main

