#!/usr/bin/env python3
"""
Setup wizard for draggg - guides users through initial setup.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import shutil
import re
from pathlib import Path
from typing import Optional, Dict, Any

import config
from gui.utils import is_wayland, get_wayland_to_x11_instructions, execute_logout
from gui.widgets import LabeledSlider, StatusIndicator, CollapsibleFrame
from setup_utils import (
    check_dependencies, detect_distribution, get_missing_dependencies,
    check_udev_rules, check_input_group, check_service_status
)


class SetupWizard:
    """Multi-step setup wizard for draggg."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("draggg Setup Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configuration data
        self.config_data = {
            'device': None,
            'threshold': 10,
            'drag_sensitivity': 0.25,
            'left_handed': False,
            'leading_finger_weight': 1.5,
            'other_fingers_weight': 0.3,
        }
        
        self.current_step = 0
        self.steps = [
            self.step_welcome_session,
            self.step_dependencies,
            self.step_permissions,
            self.step_hardware,
            self.step_configuration,
            self.step_service,
        ]
        
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress indicator
        self.progress_frame = ttk.Frame(self.main_frame)
        self.progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.back_btn = ttk.Button(self.button_frame, text="Back", command=self.prev_step, state=tk.DISABLED)
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(self.button_frame, text="Next", command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT)
        
        self.cancel_btn = ttk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Start with first step
        self.show_step(0)
    
    def clear_content(self):
        """Clear content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_progress(self):
        """Update progress indicator."""
        total = len(self.steps)
        current = self.current_step + 1
        self.progress_label.config(text=f"Step {current} of {total}")
    
    def show_step(self, step: int):
        """Show a specific step."""
        self.current_step = step
        self.clear_content()
        self.update_progress()
        
        # Enable/disable navigation buttons
        self.back_btn.config(state=tk.NORMAL if step > 0 else tk.DISABLED)
        
        # Show step content
        self.steps[step]()
    
    def next_step(self):
        """Move to next step."""
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.finish_setup()
    
    def prev_step(self):
        """Move to previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def cancel(self):
        """Cancel setup."""
        if messagebox.askyesno("Cancel Setup", "Are you sure you want to cancel setup?"):
            self.root.destroy()
    
    # Step implementations
    
    def step_welcome_session(self):
        """Step 1: Welcome and session detection."""
        title = ttk.Label(self.content_frame, text="Welcome to draggg Setup", font=("", 16, "bold"))
        title.pack(pady=(0, 20))
        
        welcome_text = (
            "This wizard will guide you through setting up three-finger drag "
            "gestures for your touchpad.\n\n"
            "Let's start by checking your system configuration."
        )
        ttk.Label(self.content_frame, text=welcome_text, wraplength=550).pack(pady=(0, 20))
        
        # Check session type
        if is_wayland():
            self.show_wayland_warning()
        else:
            ttk.Label(self.content_frame, text="✓ X11 session detected. Optimal compatibility!", 
                     foreground="green").pack(pady=10)
    
    def show_wayland_warning(self):
        """Show Wayland warning and switching instructions."""
        warning_frame = ttk.LabelFrame(self.content_frame, text="Session Type Warning", padding="10")
        warning_frame.pack(fill=tk.X, pady=10)
        
        warning_text = (
            "⚠ Wayland session detected.\n\n"
            "draggg works best with X11. For optimal functionality, "
            "please switch to an X11 session."
        )
        ttk.Label(warning_frame, text=warning_text, foreground="orange", wraplength=520).pack()
        
        btn_frame = ttk.Frame(warning_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Show Instructions to Switch to X11", 
                  command=self.show_x11_switch_dialog).pack(side=tk.LEFT, padx=(0, 10))
        
        self.continue_anyway_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(btn_frame, text="Continue anyway (limited functionality)", 
                       variable=self.continue_anyway_var).pack(side=tk.LEFT)
    
    def show_x11_switch_dialog(self):
        """Show dialog with instructions to switch to X11."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Switch to X11 Session")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        instructions = get_wayland_to_x11_instructions()
        
        # Title
        title = ttk.Label(dialog, text=instructions['title'], font=("", 14, "bold"))
        title.pack(pady=10)
        
        # Instructions
        text_frame = ttk.Frame(dialog, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=15)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', instructions['description'])
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def open_editor():
            """Open config file in editor with sudo."""
            config_path = instructions['config_file']
            # Try different methods to open editor with sudo
            for cmd in [
                f"pkexec gedit {config_path}",
                f"pkexec nano {config_path}",
                f"sudo gedit {config_path}",
                f"sudo nano {config_path}",
            ]:
                try:
                    subprocess.Popen(cmd, shell=True)
                    break
                except:
                    continue
        
        ttk.Button(btn_frame, text="Open Config File in Editor", 
                  command=open_editor).pack(side=tk.LEFT, padx=(0, 10))
        
        def copy_command():
            """Copy edit command to clipboard."""
            cmd = f"sudo nano {instructions['config_file']}"
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            messagebox.showinfo("Copied", f"Command copied to clipboard:\n{cmd}")
        
        ttk.Button(btn_frame, text="Copy Edit Command", 
                  command=copy_command).pack(side=tk.LEFT, padx=(0, 10))
        
        def proceed_to_logout():
            """Proceed to logout after file edit."""
            dialog.destroy()
            self.show_logout_confirmation()
        
        ttk.Button(btn_frame, text="I've edited the file, proceed", 
                  command=proceed_to_logout).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def show_logout_confirmation(self):
        """Show logout confirmation dialog."""
        msg = (
            "You need to log out and log back in for changes to take effect.\n\n"
            "After logging back in, your system will use X11 and draggg will work optimally.\n\n"
            "Make sure you've saved any open work.\n\n"
            "Click OK to log out now."
        )
        
        if messagebox.askokcancel("Confirm Logout", msg):
            if execute_logout():
                messagebox.showinfo("Logging Out", "You will be logged out now. Please log back in to continue setup.")
            else:
                messagebox.showerror("Error", "Could not execute logout command. Please log out manually.")
    
    def step_dependencies(self):
        """Step 2: Dependency check and installation."""
        title = ttk.Label(self.content_frame, text="Check Dependencies", font=("", 14, "bold"))
        title.pack(pady=(0, 20))
        
        deps = check_dependencies()
        missing = get_missing_dependencies()
        
        deps_frame = ttk.LabelFrame(self.content_frame, text="Dependencies", padding="10")
        deps_frame.pack(fill=tk.X, pady=10)
        
        status_frame = ttk.Frame(deps_frame)
        status_frame.pack(fill=tk.X)
        
        StatusIndicator(status_frame, "evdev", "success" if deps['evdev'] else "error").pack(anchor=tk.W, pady=2)
        StatusIndicator(status_frame, "uinput", "success" if deps['uinput'] else "error").pack(anchor=tk.W, pady=2)
        StatusIndicator(status_frame, "xdotool", "success" if deps['xdotool'] else "error").pack(anchor=tk.W, pady=2)
        
        if missing:
            ttk.Label(deps_frame, text=f"Missing: {', '.join(missing)}", 
                     foreground="red").pack(pady=(10, 0))
            
            def install_deps():
                """Install dependencies via package manager."""
                distro = detect_distribution()
                pkg_mgr_info = self._get_package_manager_commands(distro)
                
                if not pkg_mgr_info:
                    messagebox.showerror("Error", f"Unsupported distribution: {distro}")
                    return
                
                pkg_mgr, packages = pkg_mgr_info
                cmd = f"sudo {pkg_mgr} install -y {' '.join(packages)}"
                
                messagebox.showinfo("Install Dependencies", 
                    f"Please run the following command in a terminal:\n\n{cmd}\n\n"
                    "Or use your system's package manager to install:\n" +
                    "\n".join(f"  - {pkg}" for pkg in packages))
            
            ttk.Button(deps_frame, text="Install Missing Dependencies", 
                      command=install_deps).pack(pady=(10, 0))
        else:
            ttk.Label(deps_frame, text="✓ All dependencies installed!", 
                     foreground="green").pack(pady=(10, 0))
    
    def _get_package_manager_commands(self, distro: str):
        """Get package manager command for distribution."""
        from setup_utils import get_package_manager_commands as get_pkg_mgr
        return get_pkg_mgr(distro)
    
    def step_permissions(self):
        """Step 3: Permissions setup."""
        title = ttk.Label(self.content_frame, text="Setup Permissions", font=("", 14, "bold"))
        title.pack(pady=(0, 20))
        
        perms_frame = ttk.LabelFrame(self.content_frame, text="Required Permissions", padding="10")
        perms_frame.pack(fill=tk.X, pady=10)
        
        # Check udev rules
        udev_ok = check_udev_rules()
        udev_status = StatusIndicator(perms_frame, 
            "Udev rules for uinput" + (" ✓" if udev_ok else " ✗"),
            "success" if udev_ok else "warning")
        udev_status.pack(anchor=tk.W, pady=5)
        
        if not udev_ok:
            def setup_udev():
                cmd = 'echo \'KERNEL=="uinput", MODE="0666"\' | sudo tee /etc/udev/rules.d/99-uinput.rules && sudo udevadm control --reload-rules && sudo udevadm trigger'
                messagebox.showinfo("Setup Udev Rules", 
                    f"Please run this command in a terminal:\n\n{cmd}\n\n"
                    "Or the setup script will handle this automatically.")
            ttk.Button(perms_frame, text="Setup Udev Rules", 
                      command=setup_udev).pack(anchor=tk.W, pady=5)
        
        # Check input group
        input_ok = check_input_group()
        input_status = StatusIndicator(perms_frame,
            f"User in 'input' group" + (" ✓" if input_ok else " ✗"),
            "success" if input_ok else "warning")
        input_status.pack(anchor=tk.W, pady=5)
        
        if not input_ok:
            ttk.Label(perms_frame, 
                text="Note: Add user to 'input' group with: sudo usermod -a -G input $USER\n"
                     "Then log out and back in.",
                foreground="orange", wraplength=500).pack(anchor=tk.W, pady=5)
    
    def step_hardware(self):
        """Step 4: Hardware detection."""
        title = ttk.Label(self.content_frame, text="Detect Touchpad", font=("", 14, "bold"))
        title.pack(pady=(0, 20))
        
        ttk.Label(self.content_frame, 
                 text="Hardware detection will run automatically. You can also specify a device manually.",
                 wraplength=550).pack(pady=(0, 10))
        
        # Device selection
        device_frame = ttk.LabelFrame(self.content_frame, text="Touchpad Device", padding="10")
        device_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(device_frame, text="Device path:").pack(anchor=tk.W)
        
        device_entry_frame = ttk.Frame(device_frame)
        device_entry_frame.pack(fill=tk.X, pady=5)
        
        self.device_var = tk.StringVar(value="Auto-detect")
        device_entry = ttk.Entry(device_entry_frame, textvariable=self.device_var)
        device_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        def run_detection():
            """Run hardware detection."""
            import subprocess
            script_path = Path(__file__).parent.parent / "detect_hardware.py"
            try:
                subprocess.Popen(['python3', str(script_path)])
            except Exception:
                messagebox.showinfo("Hardware Detection", 
                    "Hardware detection will be run automatically when draggg starts.\n\n"
                    "You can also run: python3 detect_hardware.py")
        
        ttk.Button(device_entry_frame, text="Run Detection", 
                  command=run_detection).pack(side=tk.RIGHT)
        
        ttk.Label(device_frame, text="Leave as 'Auto-detect' for automatic detection (recommended)",
                 foreground="gray").pack(anchor=tk.W, pady=(5, 0))
    
    def step_configuration(self):
        """Step 5: Configuration settings."""
        title = ttk.Label(self.content_frame, text="Configuration", font=("", 14, "bold"))
        title.pack(pady=(0, 20))
        
        # Scrollable frame
        canvas_frame = ttk.Frame(self.content_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Movement threshold
        self.threshold_slider = LabeledSlider(
            scrollable_frame,
            "Movement Threshold:",
            from_=1, to=20, default=self.config_data.get('threshold', 10), resolution=1,
            command=lambda v: self.config_data.update({'threshold': int(v)})
        )
        self.threshold_slider.pack(fill=tk.X, pady=10)
        ttk.Label(scrollable_frame, text="How far fingers must move before dragging starts (pixels)",
                 foreground="gray", font=("", 8)).pack(anchor=tk.W)
        
        # Drag sensitivity
        self.sensitivity_slider = LabeledSlider(
            scrollable_frame,
            "Drag Sensitivity:",
            from_=0.1, to=1.0, default=self.config_data.get('drag_sensitivity', 0.25), resolution=0.01,
            command=lambda v: self.config_data.update({'drag_sensitivity': v})
        )
        self.sensitivity_slider.pack(fill=tk.X, pady=10)
        ttk.Label(scrollable_frame, text="How much cursor moves relative to finger movement",
                 foreground="gray", font=("", 8)).pack(anchor=tk.W)
        
        # Left-handed mode
        self.left_handed_var = tk.BooleanVar(value=self.config_data.get('left_handed', False))
        ttk.Checkbutton(scrollable_frame, text="Left-handed mode", 
                       variable=self.left_handed_var,
                       command=lambda: self.config_data.update({'left_handed': self.left_handed_var.get()})).pack(anchor=tk.W, pady=10)
        
        # Advanced settings
        advanced = CollapsibleFrame(scrollable_frame, "Advanced Settings")
        advanced.pack(fill=tk.X, pady=10)
        
        adv_frame = advanced.get_content_frame()
        
        self.leading_weight_slider = LabeledSlider(
            adv_frame,
            "Leading Finger Weight:",
            from_=1.0, to=2.0, default=self.config_data.get('leading_finger_weight', 1.5), resolution=0.1,
            command=lambda v: self.config_data.update({'leading_finger_weight': v})
        )
        self.leading_weight_slider.pack(fill=tk.X, pady=5)
        
        self.other_weight_slider = LabeledSlider(
            adv_frame,
            "Other Fingers Weight:",
            from_=0.2, to=0.5, default=self.config_data.get('other_fingers_weight', 0.3), resolution=0.01,
            command=lambda v: self.config_data.update({'other_fingers_weight': v})
        )
        self.other_weight_slider.pack(fill=tk.X, pady=5)
    
    def step_service(self):
        """Step 6: Service installation and shortcuts."""
        title = ttk.Label(self.content_frame, text="Service Setup", font=("", 14, "bold"))
        title.pack(pady=(0, 20))
        
        service_frame = ttk.LabelFrame(self.content_frame, text="Systemd Service", padding="10")
        service_frame.pack(fill=tk.X, pady=10)
        
        # Check current service status
        status = check_service_status()
        
        # Status display
        if status['exists']:
            status_text = f"Service exists. Enabled: {status['enabled']}, Running: {status['running']}"
            status_color = "green" if status['running'] else "orange"
            ttk.Label(service_frame, text=status_text, foreground=status_color).pack(anchor=tk.W, pady=(0, 10))
        else:
            ttk.Label(service_frame, text="Service not installed", foreground="orange").pack(anchor=tk.W, pady=(0, 10))
        
        # Service installation button
        install_btn_frame = ttk.Frame(service_frame)
        install_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        def install_service_btn():
            """Install the systemd service."""
            try:
                script_dir = Path(__file__).parent.parent
                self._install_service_file(script_dir)
                # Refresh status
                new_status = check_service_status()
                if new_status['exists']:
                    messagebox.showinfo("Success", "Service installed successfully!")
                    # Refresh UI
                    self.show_step(self.current_step)
                else:
                    messagebox.showerror("Error", "Service installation failed")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install service: {e}")
        
        if not status['exists']:
            ttk.Button(install_btn_frame, text="Install Service", command=install_service_btn).pack(side=tk.LEFT, padx=(0, 5))
        
        # Service control buttons (if service exists)
        if status['exists']:
            control_frame = ttk.Frame(service_frame)
            control_frame.pack(fill=tk.X, pady=(0, 10))
            
            def start_service_btn():
                try:
                    subprocess.run(['systemctl', '--user', 'start', 'draggg.service'], check=True)
                    messagebox.showinfo("Success", "Service started successfully!")
                    self.show_step(self.current_step)  # Refresh
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to start service: {e}")
            
            def enable_service_btn():
                try:
                    subprocess.run(['systemctl', '--user', 'enable', 'draggg.service'], check=True)
                    messagebox.showinfo("Success", "Service enabled to start on login")
                    self.show_step(self.current_step)  # Refresh
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to enable service: {e}")
            
            ttk.Button(control_frame, text="Start Service", command=start_service_btn).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(control_frame, text="Enable on Login", command=enable_service_btn).pack(side=tk.LEFT)
        
        # Auto-start option
        ttk.Label(service_frame, 
                 text="Would you like draggg to start automatically on login?",
                 wraplength=550).pack(pady=(10, 5))
        
        self.service_enable_var = tk.BooleanVar(value=status.get('enabled', False) if status['exists'] else True)
        ttk.Checkbutton(service_frame, text="Enable systemd service (start on login)", 
                       variable=self.service_enable_var).pack(anchor=tk.W)
        
        self.service_start_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(service_frame, text="Start service now after setup", 
                       variable=self.service_start_var).pack(anchor=tk.W, pady=(5, 0))
        
        # Shortcut creation options
        shortcuts_frame = ttk.LabelFrame(self.content_frame, text="Create Shortcuts", padding="10")
        shortcuts_frame.pack(fill=tk.X, pady=10)
        
        self.create_app_menu_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(shortcuts_frame, text="Create application menu entry", 
                       variable=self.create_app_menu_var).pack(anchor=tk.W, pady=2)
        
        self.create_desktop_shortcut_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(shortcuts_frame, text="Create desktop shortcut", 
                       variable=self.create_desktop_shortcut_var).pack(anchor=tk.W, pady=2)
    
    def finish_setup(self):
        """Finish setup and save configuration."""
        # Update config from UI
        if hasattr(self, 'device_var'):
            device_path = self.device_var.get()
            if device_path and device_path != "Auto-detect" and device_path.strip():
                self.config_data['device'] = device_path.strip()
            else:
                self.config_data['device'] = None
        
        if hasattr(self, 'left_handed_var'):
            self.config_data['left_handed'] = self.left_handed_var.get()
        
        # Collect slider values if they exist
        if hasattr(self, 'threshold_slider'):
            self.config_data['threshold'] = int(self.threshold_slider.get())
        if hasattr(self, 'sensitivity_slider'):
            self.config_data['drag_sensitivity'] = self.sensitivity_slider.get()
        if hasattr(self, 'leading_weight_slider'):
            self.config_data['leading_finger_weight'] = self.leading_weight_slider.get()
        if hasattr(self, 'other_weight_slider'):
            self.config_data['other_fingers_weight'] = self.other_weight_slider.get()
        
        # Handle shortcut creation if requested
        if hasattr(self, 'create_app_menu_var') or hasattr(self, 'create_desktop_shortcut_var'):
            try:
                script_dir = Path(__file__).parent.parent
                
                create_app_menu = getattr(self, 'create_app_menu_var', None) and self.create_app_menu_var.get() if hasattr(self, 'create_app_menu_var') else False
                create_desktop = getattr(self, 'create_desktop_shortcut_var', None) and self.create_desktop_shortcut_var.get() if hasattr(self, 'create_desktop_shortcut_var') else False
                
                if create_app_menu or create_desktop:
                    self._install_desktop_entry(script_dir, create_app_menu, create_desktop)
            except Exception:
                # Fail silently - shortcuts are optional
                pass
        
        # Handle service installation and management
        try:
            script_dir = Path(__file__).parent.parent
            service_status = check_service_status()
            
            # Install service file if it doesn't exist
            if not service_status['exists']:
                self._install_service_file(script_dir)
                # Re-check status
                service_status = check_service_status()
            
            # Enable service if requested
            if hasattr(self, 'service_enable_var') and self.service_enable_var.get():
                if service_status['exists']:
                    try:
                        subprocess.run(['systemctl', '--user', 'enable', 'draggg.service'], check=True)
                    except Exception as e:
                        messagebox.showwarning("Warning", f"Could not enable service: {e}")
            
            # Start service if requested
            if hasattr(self, 'service_start_var') and self.service_start_var.get():
                if service_status['exists']:
                    try:
                        subprocess.run(['systemctl', '--user', 'start', 'draggg.service'], check=True)
                    except Exception as e:
                        messagebox.showwarning("Warning", f"Could not start service: {e}")
        except Exception as e:
            # Fail silently or show warning - service is optional
            pass
        
        # Save configuration
        try:
            config.save_config(self.config_data)
            
            # Prepare completion message
            service_status = check_service_status()
            service_info = ""
            if service_status['exists']:
                if service_status.get('running'):
                    service_info = "\n✓ Service is running"
                elif hasattr(self, 'service_start_var') and self.service_start_var.get():
                    service_info = "\n⚠ Service installed but may need to be started manually"
            
            completion_msg = (
                "Configuration saved successfully!\n\n"
                "Setup is complete. You can now use draggg." + service_info + "\n\n"
            )
            
            # Add launch options
            if hasattr(self, 'service_start_var') and self.service_start_var.get() and service_status.get('running'):
                completion_msg += "The service is running in the background.\n"
            else:
                completion_msg += "You can:\n"
                completion_msg += "  • Launch GUI: python3 draggg_gui.py\n"
                completion_msg += "  • Run manually: python3 draggg.py\n"
                if service_status['exists']:
                    completion_msg += "  • Start service: systemctl --user start draggg.service\n"
            
            messagebox.showinfo("Setup Complete", completion_msg)
            
            # Ask if user wants to start the service now (if not already started)
            if hasattr(self, 'service_start_var') and self.service_start_var.get():
                if service_status['exists'] and not service_status.get('running'):
                    if messagebox.askyesno("Start Service", 
                        "Would you like to start the draggg service now?\n\n"
                        "This will enable three-finger drag gestures."):
                        try:
                            subprocess.run(['systemctl', '--user', 'start', 'draggg.service'], check=True)
                            messagebox.showinfo("Success", "Service started! Three-finger drag is now active.")
                        except Exception as e:
                            messagebox.showwarning("Warning", 
                                f"Could not start service: {e}\n\n"
                                "You can start it later with:\n"
                                "systemctl --user start draggg.service")
            
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def _install_desktop_entry(self, script_dir, create_app_menu, create_desktop):
        """Install desktop entry and shortcuts."""
        import os
        
        desktop_file = script_dir / "draggg.desktop"
        if not desktop_file.exists():
            return
        
        # Install icons to icon theme directory - all sizes needed for proper display
        icon_sizes = {
            '256x256': 'icon.png',
            '128x128': 'icon-128.png',
            '64x64': 'icon-64.png',
            '48x48': 'icon-48.png',
        }
        
        icons_installed = False
        for size, icon_filename in icon_sizes.items():
            icon_dir = Path.home() / ".local" / "share" / "icons" / "hicolor" / size / "apps"
            icon_file = script_dir / "assets" / icon_filename
            
            if icon_file.exists():
                icon_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy(icon_file, icon_dir / "draggg.png")
                    icons_installed = True
                except Exception as e:
                    print(f"Warning: Could not install {size} icon: {e}")
        
        # Also create smaller sizes from 48x48 if available (for toolbar/panel)
        icon_48 = script_dir / "assets" / "icon-48.png"
        if icon_48.exists():
            smaller_sizes = ['32x32', '24x24', '22x22', '16x16']
            for size in smaller_sizes:
                icon_dir = Path.home() / ".local" / "share" / "icons" / "hicolor" / size / "apps"
                icon_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy(icon_48, icon_dir / "draggg.png")
                    icons_installed = True
                except Exception:
                    pass  # Optional sizes
        
        # Update icon cache
        if icons_installed:
            try:
                icon_cache_dir = Path.home() / ".local" / "share" / "icons" / "hicolor"
                # Use -f flag to force update even if cache exists, -t for no timestamp check
                result = subprocess.run(['gtk-update-icon-cache', '-f', '-t', str(icon_cache_dir)], 
                                     capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    print(f"Warning: Icon cache update returned code {result.returncode}")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
            except FileNotFoundError:
                print("Warning: gtk-update-icon-cache not found. Icons may not appear until you log out/in.")
            except Exception as e:
                print(f"Warning: Could not update icon cache: {e}")
        
        # Install to application menu
        if create_app_menu:
            target_dir = Path.home() / ".local" / "share" / "applications"
            target_file = target_dir / "draggg.desktop"
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Read and update desktop file
            with open(desktop_file, 'r') as f:
                content = f.read()
            
            content = content.replace('/path/to/draggg', str(script_dir))
            
            # Update Exec line with python3 path
            python3_path = shutil.which('python3') or 'python3'
            content = re.sub(r'Exec=python3 ', f'Exec={python3_path} ', content)
            
            # Update Icon to use icon theme name
            content = re.sub(r'Icon=.*', 'Icon=draggg', content)
            
            # Write to target
            with open(target_file, 'w') as f:
                f.write(content)
            
            os.chmod(target_file, 0o755)
            
            # Update desktop database
            try:
                result = subprocess.run(['update-desktop-database', str(target_dir)], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    print(f"Warning: Desktop database update returned code {result.returncode}")
            except FileNotFoundError:
                pass  # Optional command
            except Exception as e:
                print(f"Warning: Could not update desktop database: {e}")
        
        # Install desktop shortcut
        if create_desktop:
            desktop_dir = Path.home() / "Desktop"
            # Try alternative names
            if not desktop_dir.exists():
                for alt in ["Desktop", "桌面", "Escritorio", "Рабочий стол"]:
                    alt_path = Path.home() / alt
                    if alt_path.exists():
                        desktop_dir = alt_path
                        break
            
            if desktop_dir.exists():
                desktop_shortcut = desktop_dir / "draggg.desktop"
                
                with open(desktop_file, 'r') as f:
                    content = f.read()
                
                content = content.replace('/path/to/draggg', str(script_dir))
                python3_path = shutil.which('python3') or 'python3'
                content = re.sub(r'Exec=python3 ', f'Exec={python3_path} ', content)
                content = re.sub(r'Icon=.*', 'Icon=draggg', content)
                
                with open(desktop_shortcut, 'w') as f:
                    f.write(content)
                
                os.chmod(desktop_shortcut, 0o755)
    
    def _install_service_file(self, script_dir):
        """Install systemd service file."""
        import os
        import shutil
        
        service_dir = Path.home() / ".config" / "systemd" / "user"
        service_file = service_dir / "draggg.service"
        service_template = script_dir / "draggg.service"
        
        # Create service directory
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # Get Python path
        python3_path = shutil.which('python3') or '/usr/bin/python3'
        script_path = script_dir / "draggg.py"
        config_path = Path.home() / ".config" / "three-finger-drag" / "config.json"
        
        # Read template if it exists, otherwise create from scratch
        if service_template.exists():
            with open(service_template, 'r') as f:
                service_content = f.read()
            # Replace placeholder paths
            service_content = service_content.replace('/path/to/Linux_Three_Fingers', str(script_dir))
            service_content = service_content.replace('/usr/bin/python3', python3_path)
            # Update ExecStart line
            import re
            exec_line = f"ExecStart={python3_path} {script_path} --config {config_path} --tray"
            service_content = re.sub(r'ExecStart=.*', exec_line, service_content)
            # Remove invalid User directive (only valid for system services, not user services)
            service_content = re.sub(r'^User=.*$', '', service_content, flags=re.MULTILINE)
            # Remove comment about changing paths
            service_content = re.sub(r'^# Change these paths.*$', '', service_content, flags=re.MULTILINE)
            # Remove comment lines that might be left
            service_content = re.sub(r'^# .*$', '', service_content, flags=re.MULTILINE)
            # Clean up multiple empty lines
            service_content = re.sub(r'\n\n\n+', '\n\n', service_content)
            # Clean up leading/trailing whitespace on each line
            lines = [line.rstrip() for line in service_content.split('\n')]
            service_content = '\n'.join(lines)
        else:
            # Create service file from scratch
            service_content = f"""[Unit]
Description=draggg - Linux Three-Finger Drag Gesture Handler
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
ExecStart={python3_path} {script_path} --config {config_path} --tray
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
"""
        
        # Write service file
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemd
        try:
            subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, capture_output=True)
        except Exception:
            pass  # Fail silently

