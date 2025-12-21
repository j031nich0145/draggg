#!/usr/bin/env python3
"""
Settings panel for draggg - allows users to modify settings after initial setup.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from typing import Optional, Dict, Any, List
from pathlib import Path
import os
import shutil
import re

import config
from gui.widgets import LabeledSlider, StatusIndicator, CollapsibleFrame
from setup_utils import check_service_status


class SettingsPanel:
    """Settings management panel for draggg."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("draggg Settings")
        self.root.geometry("650x600")
        self.root.resizable(True, True)
        
        # Set window icon
        self._set_window_icon()
        
        # Load current configuration
        try:
            self.config_data = config.load_config()
        except Exception:
            self.config_data = config.DEFAULT_CONFIG.copy()
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="draggg Settings", font=("", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_general_tab()
        self.create_advanced_tab()
        self.create_service_tab()
        self.create_about_tab()
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        service_status = check_service_status()
        status_text = "Service: " + ("Running" if service_status.get('running') else "Stopped")
        self.status_label = ttk.Label(status_frame, text=status_text)
        self.status_label.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Close", command=self.root.destroy).pack(side=tk.RIGHT)
    
    def create_general_tab(self):
        """Create general settings tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="General")
        
        # Movement threshold
        self.threshold_slider = LabeledSlider(
            tab,
            "Movement Threshold:",
            from_=1, to=20, default=self.config_data.get('threshold', 10), resolution=1
        )
        self.threshold_slider.pack(fill=tk.X, pady=10)
        ttk.Label(tab, text="How far fingers must move before dragging starts (pixels)",
                 foreground="gray", font=("", 8)).pack(anchor=tk.W)
        
        # Drag sensitivity
        self.sensitivity_slider = LabeledSlider(
            tab,
            "Drag Sensitivity:",
            from_=0.1, to=1.0, default=self.config_data.get('drag_sensitivity', 0.25), resolution=0.01
        )
        self.sensitivity_slider.pack(fill=tk.X, pady=10)
        ttk.Label(tab, text="How much cursor moves relative to finger movement",
                 foreground="gray", font=("", 8)).pack(anchor=tk.W)
        
        # Left-handed mode
        self.left_handed_var = tk.BooleanVar(value=self.config_data.get('left_handed', False))
        ttk.Checkbutton(tab, text="Left-handed mode", 
                       variable=self.left_handed_var).pack(anchor=tk.W, pady=10)
        
        # Device selection
        device_frame = ttk.LabelFrame(tab, text="Touchpad Device", padding="10")
        device_frame.pack(fill=tk.X, pady=10)
        
        self.device_var = tk.StringVar(value=self.config_data.get('device') or "Auto-detect")
        device_entry = ttk.Entry(device_frame, textvariable=self.device_var)
        device_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def run_detection():
            messagebox.showinfo("Hardware Detection", 
                "Run: python3 detect_hardware.py\n\n"
                "Or leave as 'Auto-detect' for automatic detection.")
        
        ttk.Button(device_frame, text="Detect", command=run_detection).pack(side=tk.RIGHT)
        
        # Desktop shortcut toggle
        shortcut_frame = ttk.LabelFrame(tab, text="Desktop Shortcut", padding="10")
        shortcut_frame.pack(fill=tk.X, pady=10)
        
        self.desktop_shortcut_var = tk.BooleanVar(value=self._check_desktop_shortcut_exists())
        ttk.Checkbutton(shortcut_frame, text="Show desktop shortcut", 
                       variable=self.desktop_shortcut_var,
                       command=self._toggle_desktop_shortcut).pack(anchor=tk.W)
    
    def create_advanced_tab(self):
        """Create advanced settings tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="Advanced")
        
        # Leading finger weight
        self.leading_weight_slider = LabeledSlider(
            tab,
            "Leading Finger Weight:",
            from_=1.0, to=2.0, default=self.config_data.get('leading_finger_weight', 1.5), resolution=0.1
        )
        self.leading_weight_slider.pack(fill=tk.X, pady=10)
        ttk.Label(tab, text="Weight for the leading finger (index finger) - higher = more influence",
                 foreground="gray", font=("", 8)).pack(anchor=tk.W)
        
        # Other fingers weight
        self.other_weight_slider = LabeledSlider(
            tab,
            "Other Fingers Weight:",
            from_=0.2, to=0.5, default=self.config_data.get('other_fingers_weight', 0.3), resolution=0.01
        )
        self.other_weight_slider.pack(fill=tk.X, pady=10)
        ttk.Label(tab, text="Weight for each of the other two fingers",
                 foreground="gray", font=("", 8)).pack(anchor=tk.W)
        
        # Device path (advanced)
        device_frame = ttk.LabelFrame(tab, text="Device Path (Advanced)", padding="10")
        device_frame.pack(fill=tk.X, pady=10)
        
        self.device_path_var = tk.StringVar(value=self.config_data.get('device') or "")
        device_path_entry = ttk.Entry(device_frame, textvariable=self.device_path_var)
        device_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(device_frame, text="Auto-detect", 
                  command=lambda: self.device_path_var.set("")).pack(side=tk.RIGHT)
    
    def create_service_tab(self):
        """Create service management tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="Service")
        
        service_status = check_service_status()
        
        # Status
        status_frame = ttk.LabelFrame(tab, text="Service Status", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        # Store reference to status indicator for updates
        if service_status['exists']:
            status_text = f"Service exists - Enabled: {service_status['enabled']}, Running: {service_status['running']}"
            self.service_status_indicator = StatusIndicator(status_frame, 
                status_text,
                "success" if service_status['running'] else "warning")
            self.service_status_indicator.pack(anchor=tk.W)
        else:
            self.service_status_indicator = StatusIndicator(status_frame, 
                "Service not installed", "error")
            self.service_status_indicator.pack(anchor=tk.W)
            
            # Show help message
            ttk.Label(status_frame, 
                text="Install the service using the setup script:\n./setup.sh",
                foreground="orange", wraplength=500).pack(anchor=tk.W, pady=(10, 0))
        
        # Controls
        controls_frame = ttk.LabelFrame(tab, text="Service Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=10)
        
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X)
        
        def start_service():
            try:
                result = subprocess.run(['systemctl', '--user', 'start', 'draggg.service'], 
                                       check=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo("Success", "Service started successfully!")
                self.update_service_status()
                # Refresh the status indicator in the Service tab
                self._refresh_service_tab_status()
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "Service start timed out. Check service status manually.")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else str(e)
                if not error_msg:
                    error_msg = f"Exit code: {e.returncode}"
                messagebox.showerror("Error", 
                    f"Failed to start service:\n\n{error_msg}\n\n"
                    "Make sure the service file exists:\n"
                    "~/.config/systemd/user/draggg.service\n\n"
                    "If not, run the setup script or GUI setup wizard to install it.")
                self.update_service_status()
                self._refresh_service_tab_status()
            except FileNotFoundError:
                messagebox.showerror("Error", "systemctl command not found. Are you running on a systemd-based system?")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start service: {type(e).__name__}: {e}")
                self.update_service_status()
                self._refresh_service_tab_status()
        
        def stop_service():
            try:
                subprocess.run(['systemctl', '--user', 'stop', 'draggg.service'], 
                             check=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo("Success", "Service stopped")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "Service stop timed out. Check service status manually.")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else str(e)
                if not error_msg:
                    error_msg = f"Exit code: {e.returncode}"
                messagebox.showerror("Error", f"Failed to stop service:\n\n{error_msg}")
                self.update_service_status()
                self._refresh_service_tab_status()
            except FileNotFoundError:
                messagebox.showerror("Error", "systemctl command not found. Are you running on a systemd-based system?")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop service: {type(e).__name__}: {e}")
                self.update_service_status()
                self._refresh_service_tab_status()
        
        def enable_service():
            try:
                subprocess.run(['systemctl', '--user', 'enable', 'draggg.service'], 
                             check=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo("Success", "Service enabled to start on login")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "Service enable timed out. Check service status manually.")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else str(e)
                if not error_msg:
                    error_msg = f"Exit code: {e.returncode}"
                messagebox.showerror("Error", f"Failed to enable service:\n\n{error_msg}")
                self.update_service_status()
                self._refresh_service_tab_status()
            except FileNotFoundError:
                messagebox.showerror("Error", "systemctl command not found. Are you running on a systemd-based system?")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to enable service: {type(e).__name__}: {e}")
                self.update_service_status()
                self._refresh_service_tab_status()
        
        def disable_service():
            try:
                subprocess.run(['systemctl', '--user', 'disable', 'draggg.service'], 
                             check=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo("Success", "Service disabled")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "Service disable timed out. Check service status manually.")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else str(e)
                if not error_msg:
                    error_msg = f"Exit code: {e.returncode}"
                messagebox.showerror("Error", f"Failed to disable service:\n\n{error_msg}")
                self.update_service_status()
                self._refresh_service_tab_status()
            except FileNotFoundError:
                messagebox.showerror("Error", "systemctl command not found. Are you running on a systemd-based system?")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to disable service: {type(e).__name__}: {e}")
                self.update_service_status()
                self._refresh_service_tab_status()
        
        def view_logs():
            """Open logs in terminal."""
            try:
                subprocess.Popen(['gnome-terminal', '--', 'journalctl', '--user', '-u', 'draggg.service', '-f'])
            except:
                messagebox.showinfo("View Logs", 
                    "Run in terminal:\njournalctl --user -u draggg.service -f")
        
        def restart_service_btn():
            """Restart service button handler."""
            try:
                # Stop first (don't fail if already stopped)
                subprocess.run(['systemctl', '--user', 'stop', 'draggg.service'], 
                             check=False, capture_output=True, text=True, timeout=10)
                # Then start
                subprocess.run(['systemctl', '--user', 'start', 'draggg.service'], 
                             check=True, capture_output=True, text=True, timeout=10)
                messagebox.showinfo("Success", "Service restarted successfully!")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.TimeoutExpired:
                messagebox.showerror("Error", "Service restart timed out. Check service status manually.")
                self.update_service_status()
                self._refresh_service_tab_status()
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else str(e)
                if not error_msg:
                    error_msg = f"Exit code: {e.returncode}"
                messagebox.showerror("Error", f"Failed to restart service:\n\n{error_msg}")
                self.update_service_status()
                self._refresh_service_tab_status()
            except FileNotFoundError:
                messagebox.showerror("Error", "systemctl command not found. Are you running on a systemd-based system?")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restart service: {type(e).__name__}: {e}")
                self.update_service_status()
                self._refresh_service_tab_status()
        
        ttk.Button(btn_frame, text="Start Service", command=start_service).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Stop Service", command=stop_service).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Restart Service", command=restart_service_btn).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Enable (Start on Login)", command=enable_service).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Disable", command=disable_service).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="View Logs", command=view_logs).pack(side=tk.LEFT)
    
    def create_about_tab(self):
        """Create about and diagnostics tab."""
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="About")
        
        # Version info
        info_frame = ttk.LabelFrame(tab, text="Version Information", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        import sys
        import os
        ttk.Label(info_frame, text=f"draggg Version: 1.0.0").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Python Version: {sys.version.split()[0]}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Session Type: {os.environ.get('XDG_SESSION_TYPE', 'unknown')}").pack(anchor=tk.W)
        
        # System info
        sys_frame = ttk.LabelFrame(tab, text="System Information", padding="10")
        sys_frame.pack(fill=tk.X, pady=10)
        
        from setup_utils import detect_distribution
        distro = detect_distribution()
        ttk.Label(sys_frame, text=f"Distribution: {distro}").pack(anchor=tk.W)
        
        # Diagnostics
        diag_frame = ttk.LabelFrame(tab, text="Diagnostics", padding="10")
        diag_frame.pack(fill=tk.X, pady=10)
        
        def run_diagnostics():
            from setup_utils import check_dependencies, check_udev_rules, check_input_group
            deps = check_dependencies()
            udev = check_udev_rules()
            input_grp = check_input_group()
            
            msg = f"Dependencies: {'OK' if deps['all_installed'] else 'MISSING'}\n"
            msg += f"Udev rules: {'OK' if udev else 'NOT CONFIGURED'}\n"
            msg += f"Input group: {'OK' if input_grp else 'NOT IN GROUP'}"
            
            messagebox.showinfo("Diagnostics", msg)
        
        ttk.Button(diag_frame, text="Run Diagnostics", command=run_diagnostics).pack(anchor=tk.W)
        
        # Uninstall section
        uninstall_frame = ttk.LabelFrame(tab, text="Uninstall", padding="10")
        uninstall_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(uninstall_frame, 
                 text="Remove draggg service, shortcuts, and icons from your system.",
                 wraplength=500).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Button(uninstall_frame, text="Uninstall draggg", 
                  command=self.uninstall_draggg).pack(anchor=tk.W)
    
    def _refresh_service_tab_status(self):
        """Refresh the service status indicator in the Service tab."""
        if hasattr(self, 'service_status_indicator'):
            status = check_service_status()
            if status['exists']:
                status_text = f"Service exists - Enabled: {status['enabled']}, Running: {status['running']}"
                self.service_status_indicator.set_status(
                    "success" if status['running'] else "warning",
                    status_text
                )
    
    def update_service_status(self):
        """Update service status display."""
        status = check_service_status()
        status_text = "Service: " + ("Running" if status.get('running') else "Stopped")
        self.status_label.config(text=status_text)
        # Also update the status in the Service tab
        self._refresh_service_tab_status()
    
    def restart_service(self):
        """Restart the draggg service."""
        try:
            # Stop first (don't fail if already stopped)
            subprocess.run(['systemctl', '--user', 'stop', 'draggg.service'], 
                         check=False, capture_output=True, text=True, timeout=10)
            # Then start
            subprocess.run(['systemctl', '--user', 'start', 'draggg.service'], 
                         check=True, capture_output=True, text=True, timeout=10)
            messagebox.showinfo("Success", "Service restarted successfully!")
            self.update_service_status()
            self._refresh_service_tab_status()
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Service restart timed out. Check service status manually.")
            self.update_service_status()
            self._refresh_service_tab_status()
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else str(e)
            if not error_msg:
                error_msg = f"Exit code: {e.returncode}"
            messagebox.showerror("Error", f"Failed to restart service:\n\n{error_msg}\n\n"
                                        "Try stopping and starting manually from the Service tab.")
            self.update_service_status()
            self._refresh_service_tab_status()
        except FileNotFoundError:
            messagebox.showerror("Error", "systemctl command not found. Are you running on a systemd-based system?")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart service: {type(e).__name__}: {e}\n\n"
                                        "Try stopping and starting manually from the Service tab.")
            self.update_service_status()
            self._refresh_service_tab_status()
    
    def save_settings(self):
        """Save current settings."""
        try:
            # Collect settings from UI
            new_config = {
                'threshold': int(self.threshold_slider.get()),
                'drag_sensitivity': self.sensitivity_slider.get(),
                'left_handed': self.left_handed_var.get(),
                'leading_finger_weight': self.leading_weight_slider.get(),
                'other_fingers_weight': self.other_weight_slider.get(),
            }
            
            # Device path
            device_path = self.device_var.get() if hasattr(self, 'device_var') else None
            if device_path and device_path != "Auto-detect":
                new_config['device'] = device_path
            else:
                new_config['device'] = None
            
            # Save
            config.save_config(new_config)
            self.config_data = new_config
            
            # Check if service is running and offer to restart it
            service_status = check_service_status()
            if service_status.get('running'):
                msg = (
                    "Settings saved successfully!\n\n"
                    "The service is currently running. "
                    "You need to restart it for the new settings to take effect.\n\n"
                    "Would you like to restart the service now?"
                )
                if messagebox.askyesno("Settings Saved", msg):
                    self.restart_service()
                else:
                    messagebox.showinfo("Note", 
                        "Settings saved. Restart the service manually:\n"
                        "systemctl --user restart draggg.service")
            else:
                messagebox.showinfo("Success", 
                    "Settings saved successfully!\n\n"
                    "Start the service to apply the new settings:\n"
                    "systemctl --user start draggg.service\n\n"
                    "Or use the 'Start Service' button in the Service tab.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _set_window_icon(self):
        """Set window icon for the GUI."""
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
            if not icon_path.exists():
                icon_path = Path(__file__).parent.parent / "assets" / "icon-48.png"
            
            if icon_path.exists():
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(False, photo)
                except ImportError:
                    # Fallback to iconbitmap if PIL not available
                    try:
                        self.root.iconbitmap(str(icon_path))
                    except Exception:
                        pass  # Icon is optional
                except Exception:
                    pass  # Icon loading is optional
        except Exception:
            pass  # Icon is optional
    
    def _check_desktop_shortcut_exists(self) -> bool:
        """Check if desktop shortcut exists."""
        desktop_dirs = [
            Path.home() / 'Desktop',
            Path.home() / '桌面',  # Chinese
            Path.home() / 'Escritorio',  # Spanish
            Path.home() / 'Рабочий стол',  # Russian
        ]
        
        for desktop_dir in desktop_dirs:
            shortcut = desktop_dir / 'draggg.desktop'
            if shortcut.exists():
                return True
        return False
    
    def _toggle_desktop_shortcut(self):
        """Toggle desktop shortcut based on checkbox state."""
        script_dir = Path(__file__).parent.parent
        desktop_file = script_dir / "draggg.desktop"
        
        if not desktop_file.exists():
            messagebox.showerror("Error", "Desktop entry template not found. Cannot create shortcut.")
            self.desktop_shortcut_var.set(False)
            return
        
        # Find desktop directory
        desktop_dirs = [
            Path.home() / 'Desktop',
            Path.home() / '桌面',  # Chinese
            Path.home() / 'Escritorio',  # Spanish
            Path.home() / 'Рабочий стол',  # Russian
        ]
        
        desktop_dir = None
        for dir_path in desktop_dirs:
            if dir_path.exists():
                desktop_dir = dir_path
                break
        
        if not desktop_dir:
            messagebox.showwarning("Warning", "Desktop directory not found. Cannot create shortcut.")
            self.desktop_shortcut_var.set(False)
            return
        
        shortcut_path = desktop_dir / "draggg.desktop"
        
        if self.desktop_shortcut_var.get():
            # Create shortcut
            try:
                # Read template
                with open(desktop_file, 'r') as f:
                    content = f.read()
                
                # Update paths
                content = content.replace('/path/to/draggg', str(script_dir))
                python3_path = shutil.which('python3') or 'python3'
                content = re.sub(r'Exec=python3 ', f'Exec={python3_path} ', content)
                content = re.sub(r'Icon=.*', 'Icon=draggg', content)
                
                # Write shortcut
                with open(shortcut_path, 'w') as f:
                    f.write(content)
                
                os.chmod(shortcut_path, 0o755)
                messagebox.showinfo("Success", f"Desktop shortcut created at {shortcut_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create desktop shortcut: {e}")
                self.desktop_shortcut_var.set(False)
        else:
            # Remove shortcut
            try:
                if shortcut_path.exists():
                    shortcut_path.unlink()
                    messagebox.showinfo("Success", "Desktop shortcut removed")
                else:
                    # Already removed
                    pass
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove desktop shortcut: {e}")
                self.desktop_shortcut_var.set(True)
    
    def reset_defaults(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Reset to Defaults", "Reset all settings to default values?"):
            try:
                config.save_config(config.DEFAULT_CONFIG)
                self.config_data = config.DEFAULT_CONFIG.copy()
                messagebox.showinfo("Success", "Settings reset to defaults. Please restart the application.")
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def uninstall_draggg(self):
        """Uninstall draggg service, shortcuts, and icons."""
        # Check what's installed
        home = Path.home()
        items_to_remove = []
        
        # Service file
        service_file = home / '.config' / 'systemd' / 'user' / 'draggg.service'
        if service_file.exists():
            items_to_remove.append(("Service file", str(service_file)))
        
        # Desktop entry (application menu)
        desktop_entry = home / '.local' / 'share' / 'applications' / 'draggg.desktop'
        if desktop_entry.exists():
            items_to_remove.append(("Application menu entry", str(desktop_entry)))
        
        # Desktop shortcut
        desktop_dirs = [
            home / 'Desktop',
            home / '桌面',  # Chinese
            home / 'Escritorio',  # Spanish
            home / 'Рабочий стол',  # Russian
        ]
        for desktop_dir in desktop_dirs:
            desktop_shortcut = desktop_dir / 'draggg.desktop'
            if desktop_shortcut.exists():
                items_to_remove.append(("Desktop shortcut", str(desktop_shortcut)))
                break  # Only one desktop shortcut expected
        
        # Icons
        icon_base = home / '.local' / 'share' / 'icons' / 'hicolor'
        icon_sizes = ['256x256', '128x128', '64x64', '48x48', '32x32', '16x16']
        for size in icon_sizes:
            icon_path = icon_base / size / 'apps' / 'draggg.png'
            if icon_path.exists():
                items_to_remove.append(("Icon", str(icon_path)))
        
        # Config file (optional)
        config_file = home / '.config' / 'three-finger-drag' / 'config.json'
        config_exists = config_file.exists()
        
        if not items_to_remove and not config_exists:
            messagebox.showinfo("Nothing to Remove", 
                              "No draggg components found to uninstall.")
            return
        
        # Build confirmation message
        msg = "The following will be removed:\n\n"
        for item_type, item_path in items_to_remove:
            msg += f"  • {item_type}\n"
        
        if config_exists:
            msg += "\nAdditionally, you can choose to remove the configuration file."
        
        msg += "\n\nThis will NOT remove the draggg program files themselves.\n"
        msg += "Do you want to continue?"
        
        if not messagebox.askyesno("Uninstall draggg", msg):
            return
        
        # Ask about config file
        remove_config = False
        if config_exists:
            remove_config = messagebox.askyesno("Remove Configuration", 
                                              "Also remove the configuration file?\n\n"
                                              f"{config_file}\n\n"
                                              "If you keep it, your settings will be preserved for future use.")
        
        # Perform removal
        removed = []
        errors = []
        
        try:
            # Stop and disable service first
            if service_file.exists():
                try:
                    subprocess.run(['systemctl', '--user', 'stop', 'draggg.service'], 
                                 check=False, capture_output=True, timeout=5)
                    subprocess.run(['systemctl', '--user', 'disable', 'draggg.service'], 
                                 check=False, capture_output=True, timeout=5)
                except Exception:
                    pass  # Continue even if service commands fail
            
            # Remove files
            for item_type, item_path in items_to_remove:
                try:
                    path = Path(item_path)
                    if path.is_file():
                        path.unlink()
                        removed.append(item_type)
                    elif path.is_dir():
                        shutil.rmtree(path)
                        removed.append(item_type)
                except Exception as e:
                    errors.append(f"{item_type}: {e}")
            
            # Remove config if requested
            if remove_config and config_exists:
                try:
                    config_file.unlink()
                    removed.append("Configuration file")
                except Exception as e:
                    errors.append(f"Configuration file: {e}")
            
            # Update icon cache
            if any('Icon' in item for item in removed):
                try:
                    subprocess.run(['gtk-update-icon-cache', str(icon_base)], 
                                 check=False, capture_output=True, timeout=10)
                except Exception:
                    pass  # Icon cache update is optional
            
            # Update desktop database
            if any('Application menu entry' in item or 'Desktop shortcut' in item for item in removed):
                apps_dir = home / '.local' / 'share' / 'applications'
                if apps_dir.exists():
                    try:
                        subprocess.run(['update-desktop-database', str(apps_dir)], 
                                     check=False, capture_output=True, timeout=10)
                    except Exception:
                        pass  # Desktop database update is optional
            
            # Show results
            if errors:
                msg = f"Removed: {', '.join(removed)}\n\n"
                msg += "Errors:\n" + "\n".join(f"  • {e}" for e in errors)
                messagebox.showwarning("Uninstall Complete (with errors)", msg)
            else:
                msg = f"Successfully removed:\n  • {chr(10).join('  • ' + item for item in removed)}"
                messagebox.showinfo("Uninstall Complete", msg)
                
                # Update service status display
                self.update_service_status()
                self._refresh_service_tab_status()
                
        except Exception as e:
            messagebox.showerror("Uninstall Error", f"An error occurred during uninstall: {e}")

