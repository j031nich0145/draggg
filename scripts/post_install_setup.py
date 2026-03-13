#!/usr/bin/env python3
"""
Interactive Post-Installation Setup Script for draggg
Handles PATH configuration, Wayland conversion, and desktop integration.
"""
from __future__ import annotations

import os
import sys
import shutil
import subprocess
import re
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_success(text: str):
    """Print a success message."""
    print(f"✓ {text}")


def print_warning(text: str):
    """Print a warning message."""
    print(f"⚠ {text}")


def print_info(text: str):
    """Print an info message."""
    print(f"ℹ {text}")


def print_error(text: str):
    """Print an error message."""
    print(f"✗ {text}")


def prompt_yes_no(prompt: str, default: str = "y") -> bool:
    """Prompt user for yes/no input."""
    if default.lower() == "y":
        full_prompt = f"{prompt} [Y/n]: "
    else:
        full_prompt = f"{prompt} [y/N]: "
    
    while True:
        try:
            response = input(full_prompt).strip().lower()
            if not response:
                response = default.lower()
            
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no"):
                return False
            else:
                print("Please answer 'y' or 'n'")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return False


def detect_shell() -> Tuple[str, Path]:
    """Detect user's shell and return shell name and config file path."""
    shell = os.environ.get("SHELL", "")
    
    # Try to get shell from process
    if not shell:
        try:
            import psutil
            shell = psutil.Process().exe()
        except (ImportError, Exception):
            # Fallback: try reading /proc/$$/comm
            try:
                with open(f"/proc/{os.getpid()}/comm", "r") as f:
                    shell = f.read().strip()
            except Exception:
                pass
    
    shell_name = Path(shell).name if shell else "bash"
    
    # Determine config file based on shell
    home = Path.home()
    config_files = {
        "bash": [home / ".bashrc", home / ".bash_profile"],
        "zsh": [home / ".zshrc"],
        "fish": [home / ".config" / "fish" / "config.fish"],
        "csh": [home / ".cshrc"],
        "tcsh": [home / ".tcshrc"],
    }
    
    # Try to find existing config file
    if shell_name in config_files:
        for config_file in config_files[shell_name]:
            if config_file.exists():
                return shell_name, config_file
    
    # Return default config file for shell
    if shell_name in config_files:
        return shell_name, config_files[shell_name][0]
    
    # Fallback to .profile
    return "generic", home / ".profile"


def is_in_path(scripts_dir: Path) -> bool:
    """Check if scripts directory is already in PATH."""
    path_dirs = os.environ.get("PATH", "").split(":")
    return str(scripts_dir) in path_dirs


def add_to_path(shell: str, scripts_dir: Path, config_file: Path) -> bool:
    """Add scripts directory to PATH in shell config file."""
    path_line = f'export PATH="$HOME/.local/bin:$PATH"'
    
    # Check if already in PATH
    if is_in_path(scripts_dir):
        print_info(f"{scripts_dir} is already in your PATH")
        return True
    
    # Check if already in config file
    if config_file.exists():
        try:
            content = config_file.read_text()
            if scripts_dir.as_posix() in content or "$HOME/.local/bin" in content:
                print_info(f"PATH configuration already exists in {config_file}")
                return True
        except Exception:
            pass
    
    # Special handling for fish shell
    if shell == "fish":
        # Try using fish_add_path command first
        try:
            result = subprocess.run(
                ["fish", "-c", f"fish_add_path {scripts_dir}"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print_success(f"Added {scripts_dir} to PATH using fish_add_path")
                return True
        except Exception:
            pass
        
        # Fallback: add to config.fish
        path_line = f'set -U fish_user_paths $HOME/.local/bin $fish_user_paths'
    
    # Add to config file
    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to file
        with open(config_file, "a") as f:
            f.write(f"\n# Added by draggg post-install setup\n")
            f.write(f"{path_line}\n")
        
        print_success(f"Added {scripts_dir} to PATH in {config_file}")
        print_info(f"Run 'source {config_file}' or open a new terminal to use commands")
        return True
    except Exception as e:
        print_error(f"Could not add to PATH: {e}")
        print_info(f"Manually add this line to {config_file}:")
        print_info(f"  {path_line}")
        return False


def check_wayland() -> bool:
    """Check if running on Wayland session."""
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown").lower()
    return session_type == "wayland"


def offer_wayland_conversion() -> bool:
    """Offer to convert Wayland to X11."""
    print_header("Session Type Check")
    
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    print_info(f"Current session: {session_type}")
    
    if session_type.lower() == "wayland":
        print_warning("draggg works best with X11")
        print_info("Wayland support is limited. For optimal functionality, switch to X11.")
        print()
        
        if prompt_yes_no("Would you like to convert to X11 now?", "y"):
            print_info("Launching Wayland to X11 conversion helper...")
            try:
                # Try to import and run wayland-to-x11-tui
                from scripts.wayland_to_x11_tui import main as wayland_tui_main
                wayland_tui_main()
                return True
            except Exception as e:
                print_error(f"Could not launch conversion helper: {e}")
                print_info("You can run 'wayland-to-x11-tui' manually later")
                return False
        else:
            print_info("You can convert later by running: wayland-to-x11-tui")
            return False
    elif session_type.lower() == "x11":
        print_success("X11 session detected - optimal compatibility")
        return True
    else:
        print_warning(f"Unknown session type: {session_type}")
        return False


def get_scripts_directory() -> Optional[Path]:
    """Get the directory where pip installed scripts."""
    try:
        import site
        user_base = Path(site.getuserbase())
        scripts_dir = user_base / "bin"
        return scripts_dir if scripts_dir.exists() else None
    except Exception:
        return None


def install_desktop_files() -> bool:
    """Install desktop entry and icons."""
    print_header("Desktop Integration")
    
    # Check if desktop file already exists in user directory
    desktop_file = Path.home() / ".local" / "share" / "applications" / "draggg.desktop"
    if desktop_file.exists():
        print_info("Desktop entry already exists")
        if not prompt_yes_no("Reinstall desktop entry?", "n"):
            # Still install icons and update cache
            install_icons()
            update_desktop_database()
            return True
    
    # Find installed desktop file from pip installation
    import site
    user_base = Path(site.getuserbase())
    installed_desktop = user_base / "share" / "applications" / "draggg.desktop"
    
    # Also check if we can find it in the package installation
    if not installed_desktop.exists():
        # Try to find it relative to the script location
        try:
            script_dir = Path(__file__).parent.parent
            potential_desktop = script_dir / "draggg.desktop"
            if potential_desktop.exists():
                installed_desktop = potential_desktop
        except Exception:
            pass
    
    if not installed_desktop.exists():
        print_warning("Desktop file not found in installation")
        print_info("Desktop entry will be created when you run draggg-gui")
        # Still try to install icons if available
        install_icons()
        return False
    
    # Install application menu entry
    if prompt_yes_no("Install application menu entry?", "y"):
        target_dir = Path.home() / ".local" / "share" / "applications"
        target_file = target_dir / "draggg.desktop"
        
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Read desktop file and ensure it uses entry points
            with open(installed_desktop, 'r') as f:
                content = f.read()
            
            # Ensure Exec uses draggg-gui command (entry point)
            import re
            if 'Exec=draggg-gui' not in content:
                content = re.sub(r'Exec=.*', 'Exec=draggg-gui', content)
            
            # Ensure Icon is set correctly
            if 'Icon=draggg' not in content:
                content = re.sub(r'Icon=.*', 'Icon=draggg', content)
            
            # Write to target
            with open(target_file, 'w') as f:
                f.write(content)
            
            os.chmod(target_file, 0o755)
            print_success(f"Desktop entry installed: {target_file}")
        except Exception as e:
            print_error(f"Could not install desktop entry: {e}")
            return False
    
    # Install desktop shortcut
    if prompt_yes_no("Install desktop shortcut?", "n"):
        desktop_dirs = [
            Path.home() / "Desktop",
            Path.home() / "桌面",  # Chinese
            Path.home() / "Escritorio",  # Spanish
            Path.home() / "Рабочий стол",  # Russian
        ]
        
        desktop_dir = None
        for dir_path in desktop_dirs:
            if dir_path.exists():
                desktop_dir = dir_path
                break
        
        if desktop_dir:
            shortcut_file = desktop_dir / "draggg.desktop"
            try:
                shutil.copy2(installed_desktop, shortcut_file)
                os.chmod(shortcut_file, 0o755)
                print_success(f"Desktop shortcut created: {shortcut_file}")
            except Exception as e:
                print_error(f"Could not create desktop shortcut: {e}")
        else:
            print_warning("Desktop directory not found, skipping shortcut")
    
    # Install icons (they should already be installed, but verify)
    install_icons()
    
    # Update desktop database
    update_desktop_database()
    
    return True


def install_icons() -> bool:
    """Install icons to icon theme directory."""
    import site
    
    user_base = Path(site.getuserbase())
    icon_base = user_base / "share" / "icons" / "hicolor"
    
    # Check if icons are already installed
    icon_256 = icon_base / "256x256" / "apps" / "draggg.png"
    if icon_256.exists():
        print_info("Icons already installed")
        return True
    
    # Icons should be installed by pip, but verify
    icon_sizes = ["256x256", "128x128", "64x64", "48x48"]
    icons_found = []
    
    for size in icon_sizes:
        icon_path = icon_base / size / "apps" / "draggg.png"
        if icon_path.exists():
            icons_found.append(size)
    
    if icons_found:
        print_success(f"Icons found: {', '.join(icons_found)}")
    else:
        print_warning("Icons not found - they may be installed system-wide")
    
    # Update icon cache
    update_icon_cache()
    
    return len(icons_found) > 0


def update_icon_cache() -> bool:
    """Update icon cache."""
    icon_cache_dir = Path.home() / ".local" / "share" / "icons" / "hicolor"
    
    if not icon_cache_dir.exists():
        return False
    
    try:
        result = subprocess.run(
            ["gtk-update-icon-cache", "-f", "-t", str(icon_cache_dir)],
            capture_output=True,
            timeout=30
        )
        if result.returncode == 0:
            print_success("Icon cache updated")
            return True
        else:
            print_warning("Icon cache update had warnings (this is usually OK)")
            return True
    except FileNotFoundError:
        print_warning("gtk-update-icon-cache not found - icons may not appear until logout")
        return False
    except Exception as e:
        print_warning(f"Could not update icon cache: {e}")
        return False


def update_desktop_database() -> bool:
    """Update desktop database."""
    apps_dir = Path.home() / ".local" / "share" / "applications"
    
    if not apps_dir.exists():
        return False
    
    try:
        result = subprocess.run(
            ["update-desktop-database", str(apps_dir)],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0:
            print_success("Desktop database updated")
            return True
    except FileNotFoundError:
        # Command not available - not critical
        return False
    except Exception as e:
        print_warning(f"Could not update desktop database: {e}")
        return False
    
    return False


def check_input_group() -> bool:
    """Check if the current user is in the 'input' group."""
    import grp
    try:
        user = os.getenv("USER") or os.getenv("LOGNAME") or os.popen("whoami").read().strip()
        input_group = grp.getgrnam("input")
        return user in input_group.gr_mem
    except KeyError:
        return False
    except Exception:
        return False


def setup_input_permissions() -> bool:
    """Add user to input group and install udev rule for /dev/uinput."""
    print_header("Input Device Permissions")

    in_group = check_input_group()
    if in_group:
        print_success("User is already in the 'input' group")
    else:
        print_warning("User is NOT in the 'input' group.")
        print_info("draggg needs read access to touchpad event devices.")
        print()
        if prompt_yes_no("Add current user to 'input' group? (requires sudo)", "y"):
            try:
                user = os.getenv("USER") or os.popen("whoami").read().strip()
                result = subprocess.run(
                    ["sudo", "usermod", "-aG", "input", user],
                    check=True
                )
                print_success("Added to 'input' group.")
                print_warning("You must LOG OUT and LOG BACK IN for this to take effect.")
            except subprocess.CalledProcessError as e:
                print_error(f"Could not add to group: {e}")
                print_info("Run manually:  sudo usermod -aG input $USER")
        else:
            print_info("Skipped. You can add yourself later:  sudo usermod -aG input $USER")

    # udev rule for /dev/uinput
    udev_rule_path = Path("/etc/udev/rules.d/99-draggg.rules")
    uinput_rule = 'KERNEL=="uinput", GROUP="input", MODE="0660"\n'

    if udev_rule_path.exists():
        try:
            existing = udev_rule_path.read_text()
            if "uinput" in existing and "input" in existing:
                print_success("udev rule for /dev/uinput already in place")
                return True
        except Exception:
            pass

    print()
    print_info("A udev rule is needed so /dev/uinput is writable by the 'input' group.")
    if prompt_yes_no(f"Install udev rule to {udev_rule_path}? (requires sudo)", "y"):
        try:
            # Write via tee so sudo is used for the privileged write
            proc = subprocess.run(
                ["sudo", "tee", str(udev_rule_path)],
                input=uinput_rule,
                text=True,
                capture_output=True,
                check=True
            )
            subprocess.run(["sudo", "udevadm", "control", "--reload-rules"], check=True)
            subprocess.run(["sudo", "udevadm", "trigger"], check=True)
            print_success(f"udev rule installed: {udev_rule_path}")
        except subprocess.CalledProcessError as e:
            print_error(f"Could not install udev rule: {e}")
            print_info(f"Run manually:")
            print_info(f'  echo \'{uinput_rule.strip()}\' | sudo tee {udev_rule_path}')
            print_info(f"  sudo udevadm control --reload-rules && sudo udevadm trigger")
    else:
        print_info("Skipped. draggg may not be able to create virtual pointer events.")

    return True


def find_service_source() -> Optional[Path]:
    """Find the draggg.service file from the installed package or source tree."""
    import site

    candidates = []

    # Installed via pip: look in the package data dir
    for path in sys.path:
        candidate = Path(path) / "draggg.service"
        candidates.append(candidate)
        # Also inside package subdirectory
        candidate2 = Path(path) / "draggg" / "draggg.service"
        candidates.append(candidate2)

    # Relative to this script (source / editable install)
    candidates.append(Path(__file__).parent.parent / "draggg.service")

    # User site data
    try:
        user_data = Path(site.getuserbase()) / "share" / "draggg" / "draggg.service"
        candidates.append(user_data)
    except Exception:
        pass

    for c in candidates:
        if c.exists():
            return c

    return None


def setup_systemd_service() -> bool:
    """Install and enable the draggg systemd user service."""
    print_header("Background Service Setup")

    service_dest_dir = Path.home() / ".config" / "systemd" / "user"
    service_dest = service_dest_dir / "draggg.service"

    # Check if already installed
    if service_dest.exists():
        print_info(f"Service already installed at {service_dest}")
        if not prompt_yes_no("Reinstall / overwrite service file?", "n"):
            # Still offer enable/start
            _enable_and_start_service()
            return True

    # Find source service file
    source = find_service_source()
    if not source:
        print_error("Could not find draggg.service in installed package.")
        print_info("Make sure draggg is fully installed:  pip install --user draggg")
        return False

    # Install
    try:
        service_dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, service_dest)
        print_success(f"Service file installed: {service_dest}")
    except Exception as e:
        print_error(f"Could not install service file: {e}")
        return False

    _enable_and_start_service()
    return True


def _enable_and_start_service():
    """Run systemctl --user daemon-reload and enable/start draggg."""
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        print_success("systemd user daemon reloaded")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print_warning(f"daemon-reload failed: {e}")
        return

    if prompt_yes_no("Enable draggg service to start on login?", "y"):
        try:
            subprocess.run(["systemctl", "--user", "enable", "draggg"], check=True)
            print_success("draggg service enabled (starts on login)")
        except subprocess.CalledProcessError as e:
            print_error(f"Could not enable service: {e}")

    if prompt_yes_no("Start draggg service now?", "y"):
        try:
            subprocess.run(["systemctl", "--user", "start", "draggg"], check=True)
            print_success("draggg service started")
        except subprocess.CalledProcessError as e:
            print_error(f"Could not start service: {e}")
            print_info("Check status with:  systemctl --user status draggg")


def launch_gui_now():
    """Offer to launch draggg-gui immediately."""
    print_header("Launch GUI")
    print_info("The draggg GUI lets you tune sensitivity, button mapping, and more.")
    if not prompt_yes_no("Launch draggg-gui now?", "y"):
        print_info("You can launch it any time by running: draggg-gui")
        return

    gui_cmd = shutil.which("draggg-gui")
    if not gui_cmd:
        local_bin = Path.home() / ".local" / "bin" / "draggg-gui"
        if local_bin.exists():
            gui_cmd = str(local_bin)

    if not gui_cmd:
        print_error("draggg-gui not found. Make sure ~/.local/bin is in your PATH.")
        return

    try:
        subprocess.Popen([gui_cmd], start_new_session=True)
        print_success("draggg-gui launched")
    except Exception as e:
        print_error(f"Could not launch draggg-gui: {e}")
        print_info(f"Try running it directly:  {gui_cmd}")


def main():
    """Interactive terminal setup wizard for draggg."""
    print_header("draggg Setup Wizard")

    print("Welcome! This wizard will configure draggg step by step.")
    print("You can skip any step by answering 'n'.")
    print()

    # ------------------------------------------------------------------ #
    # Step 1: PATH                                                         #
    # ------------------------------------------------------------------ #
    print_header("Step 1 of 5 — PATH Configuration")
    scripts_dir = get_scripts_directory() or (Path.home() / ".local" / "bin")
    print_info(f"draggg scripts are installed in: {scripts_dir}")

    if is_in_path(scripts_dir):
        print_success("Already in PATH — no action needed")
    else:
        shell, config_file = detect_shell()
        print_info(f"Detected shell: {shell}")
        print_info(f"Config file:    {config_file}")
        print()
        if prompt_yes_no(f"Add {scripts_dir} to PATH in {config_file}?", "y"):
            add_to_path(shell, scripts_dir, config_file)
        else:
            print_info("Skipped. Add manually:")
            print_info(f'  export PATH="{scripts_dir}:$PATH"')

    # ------------------------------------------------------------------ #
    # Step 2: Input device permissions                                     #
    # ------------------------------------------------------------------ #
    print_header("Step 2 of 5 — Input Device Permissions")
    setup_input_permissions()

    # ------------------------------------------------------------------ #
    # Step 3: Systemd user service                                         #
    # ------------------------------------------------------------------ #
    print_header("Step 3 of 5 — Background Service")
    if shutil.which("systemctl") is None:
        print_warning("systemctl not found — skipping service setup.")
        print_info("You can start draggg manually:  draggg &")
    else:
        setup_systemd_service()

    # ------------------------------------------------------------------ #
    # Step 4: Desktop integration                                          #
    # ------------------------------------------------------------------ #
    print_header("Step 4 of 5 — Desktop Integration")
    install_desktop_files()

    # ------------------------------------------------------------------ #
    # Step 5: Wayland check                                                #
    # ------------------------------------------------------------------ #
    print_header("Step 5 of 5 — Session Type")
    if check_wayland():
        offer_wayland_conversion()
    else:
        session = os.environ.get("XDG_SESSION_TYPE", "unknown")
        print_success(f"Session type: {session} — no conversion needed")

    # ------------------------------------------------------------------ #
    # Optional: Launch GUI                                                 #
    # ------------------------------------------------------------------ #
    launch_gui_now()

    # ------------------------------------------------------------------ #
    # Summary                                                              #
    # ------------------------------------------------------------------ #
    print_header("Setup Complete!")
    print_success("draggg is configured and ready to use.")
    print()
    print("Quick reference:")
    print("  draggg          — start the gesture handler")
    print("  draggg-gui      — open the settings GUI")
    print("  draggg-setup    — re-run this wizard")
    print("  draggg --help   — show all options")
    print()
    print("If you added PATH or joined the input group, open a new terminal")
    print("(or log out and back in) for the changes to take effect.")
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
