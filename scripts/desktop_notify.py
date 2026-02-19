#!/usr/bin/env python3
"""
Desktop notification system for draggg.
Supports Linux desktop notifications with action buttons.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple


def send_notification(
    title: str,
    message: str,
    icon: Optional[str] = None,
    urgency: str = "normal",
    timeout: int = 10000,
    actions: Optional[Dict[str, str]] = None
) -> bool:
    """
    Send a desktop notification.
    
    Args:
        title: Notification title
        message: Notification message
        icon: Path to icon file (optional)
        urgency: Notification urgency (low, normal, critical)
        timeout: Timeout in milliseconds
        actions: Dictionary of action_id -> action_label pairs
    
    Returns:
        True if notification was sent successfully, False otherwise
    """
    # Try notify-send first (most common on Linux)
    if _try_notify_send(title, message, icon, urgency, timeout, actions):
        return True
    
    # Try Python notify2 library
    if _try_notify2(title, message, icon, urgency, timeout, actions):
        return True
    
    # Try dbus-python directly
    if _try_dbus_python(title, message, icon, urgency, timeout, actions):
        return True
    
    # Fallback: print to stderr (for non-GUI environments)
    print(f"[Notification] {title}: {message}", file=sys.stderr)
    return False


def _try_notify_send(
    title: str,
    message: str,
    icon: Optional[str],
    urgency: str,
    timeout: int,
    actions: Optional[Dict[str, str]]
) -> bool:
    """Try using notify-send command."""
    try:
        cmd = ["notify-send", "--urgency", urgency]
        
        if icon:
            cmd.extend(["--icon", icon])
        
        if timeout:
            cmd.extend(["--expire-time", str(timeout)])
        
        # Add actions if supported (requires notify-send with --action support)
        if actions:
            for action_id, action_label in actions.items():
                cmd.extend(["--action", f"{action_id},{action_label}"])
        
        cmd.extend([title, message])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception:
        return False


def _try_notify2(
    title: str,
    message: str,
    icon: Optional[str],
    urgency: str,
    timeout: int,
    actions: Optional[Dict[str, str]]
) -> bool:
    """Try using notify2 Python library."""
    try:
        import notify2
        
        # Initialize notify2
        notify2.init("draggg")
        
        # Create notification
        n = notify2.Notification(title, message)
        
        if icon:
            n.set_icon_from_path(icon)
        
        # Set urgency
        urgency_map = {
            "low": notify2.URGENCY_LOW,
            "normal": notify2.URGENCY_NORMAL,
            "critical": notify2.URGENCY_CRITICAL
        }
        n.set_urgency(urgency_map.get(urgency, notify2.URGENCY_NORMAL))
        
        # Set timeout (convert ms to seconds)
        if timeout:
            n.set_timeout(timeout // 1000)
        
        # Add actions if supported
        if actions:
            for action_id, action_label in actions.items():
                n.add_action(action_id, action_label, _action_callback)
        
        # Show notification
        n.show()
        return True
    except ImportError:
        return False
    except Exception:
        return False


def _try_dbus_python(
    title: str,
    message: str,
    icon: Optional[str],
    urgency: str,
    timeout: int,
    actions: Optional[Dict[str, str]]
) -> bool:
    """Try using dbus-python directly."""
    try:
        import dbus
        
        bus = dbus.SessionBus()
        notify_obj = bus.get_object(
            "org.freedesktop.Notifications",
            "/org/freedesktop/Notifications"
        )
        notify_iface = dbus.Interface(
            notify_obj,
            "org.freedesktop.Notifications"
        )
        
        # Prepare hints
        hints = {}
        if icon:
            hints["image-path"] = dbus.String(icon)
        
        urgency_map = {
            "low": 0,
            "normal": 1,
            "critical": 2
        }
        hints["urgency"] = dbus.Byte(urgency_map.get(urgency, 1))
        
        # Prepare actions (list of pairs: action_id, action_label)
        action_list = []
        if actions:
            for action_id, action_label in actions.items():
                action_list.append(action_id)
                action_list.append(action_label)
        
        # Call Notify
        notify_iface.Notify(
            "draggg",  # app_name
            0,  # replaces_id
            icon or "",  # app_icon
            title,  # summary
            message,  # body
            action_list,  # actions
            hints,  # hints
            timeout  # expire_timeout
        )
        return True
    except ImportError:
        return False
    except Exception:
        return False


def _action_callback(n, action_id):
    """Callback for notify2 actions."""
    # Store action in a file for the main script to read
    action_file = Path.home() / ".config" / "draggg" / "notification_action"
    action_file.parent.mkdir(parents=True, exist_ok=True)
    action_file.write_text(action_id)


def wait_for_notification_response(
    action_file: Optional[Path] = None,
    timeout: int = 30
) -> Optional[str]:
    """
    Wait for user to click a notification action button.
    
    Args:
        action_file: Path to file where action ID will be written
        timeout: Maximum time to wait in seconds
    
    Returns:
        Action ID if user clicked a button, None otherwise
    """
    if action_file is None:
        action_file = Path.home() / ".config" / "draggg" / "notification_action"
    
    # Remove old action file if it exists
    if action_file.exists():
        action_file.unlink()
    
    # Wait for action file to be created
    start_time = time.time()
    while time.time() - start_time < timeout:
        if action_file.exists():
            try:
                action_id = action_file.read_text().strip()
                action_file.unlink()  # Clean up
                return action_id
            except Exception:
                pass
        time.sleep(0.5)
    
    return None


def send_notification_with_response(
    title: str,
    message: str,
    actions: Dict[str, str],
    icon: Optional[str] = None,
    timeout: int = 30
) -> Optional[str]:
    """
    Send a notification and wait for user response.
    
    Args:
        title: Notification title
        message: Notification message
        actions: Dictionary of action_id -> action_label pairs
        icon: Path to icon file (optional)
        timeout: Maximum time to wait for response in seconds
    
    Returns:
        Action ID if user clicked a button, None otherwise
    """
    # Send notification
    send_notification(
        title=title,
        message=message,
        icon=icon,
        actions=actions,
        timeout=timeout * 1000  # Convert to milliseconds
    )
    
    # Wait for response
    return wait_for_notification_response(timeout=timeout)


def get_icon_path() -> Optional[Path]:
    """Get path to draggg icon."""
    # Try multiple locations
    icon_paths = [
        Path.home() / ".local" / "share" / "icons" / "hicolor" / "128x128" / "apps" / "draggg.png",
        Path.home() / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "draggg.png",
        Path(__file__).parent.parent / "assets" / "icon-128.png",
        Path(__file__).parent.parent / "assets" / "icon.png",
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            return icon_path
    
    return None


if __name__ == "__main__":
    # Test notification
    icon_path = get_icon_path()
    actions = {
        "yes": "Yes",
        "no": "No"
    }
    
    response = send_notification_with_response(
        title="draggg Test",
        message="This is a test notification. Click a button:",
        actions=actions,
        icon=str(icon_path) if icon_path else None
    )
    
    if response:
        print(f"User clicked: {response}")
    else:
        print("No response received")
