#!/usr/bin/env python3
"""
Hardware Detection Utility for Linux Three-Finger Drag
Detects and lists available touchpad devices with compatibility information.
"""

import os
import sys
import subprocess
from typing import List, Dict, Optional, Tuple

try:
    from evdev import InputDevice, ecodes, list_devices
except ImportError:
    print("Error: python3-evdev not installed")
    print("Install with: sudo apt install python3-evdev")
    sys.exit(1)

class TouchpadDetector:
    """Detects and analyzes touchpad devices."""
    
    ABS_MT_SLOT = ecodes.ABS_MT_SLOT
    ABS_MT_TRACKING_ID = ecodes.ABS_MT_TRACKING_ID
    ABS_MT_POSITION_X = ecodes.ABS_MT_POSITION_X
    ABS_MT_POSITION_Y = ecodes.ABS_MT_POSITION_Y
    ABS_X = ecodes.ABS_X
    ABS_Y = ecodes.ABS_Y
    
    def __init__(self):
        self.compatible_devices: List[Dict] = []
        self.incompatible_devices: List[Dict] = []
    
    def is_touchpad(self, device: InputDevice) -> Tuple[bool, str]:
        """
        Check if device is a compatible touchpad.
        Returns (is_compatible, reason)
        """
        try:
            capabilities = device.capabilities()
        except (OSError, PermissionError) as e:
            return False, f"Permission denied: {e}"
        
        # Check for ABS events (required for touchpads)
        if ecodes.EV_ABS not in capabilities:
            return False, "No absolute axis events (EV_ABS)"
        
        abs_caps = [cap[0] if isinstance(cap, tuple) else cap 
                   for cap in capabilities[ecodes.EV_ABS]]
        
        device_name = device.name.lower()
        
        # Apple trackpad detection (bcm5974)
        is_apple = 'bcm5974' in device_name or 'apple' in device_name
        if is_apple and ecodes.EV_ABS in capabilities:
            return True, "Apple trackpad (bcm5974) - Compatible"
        
        # Standard touchpad detection
        has_mt_slot = self.ABS_MT_SLOT in abs_caps
        has_mt_tracking = self.ABS_MT_TRACKING_ID in abs_caps
        has_position = (
            self.ABS_MT_POSITION_X in abs_caps or
            self.ABS_X in abs_caps
        )
        
        if has_mt_slot and has_mt_tracking and has_position:
            return True, "Standard multi-touch touchpad - Compatible"
        
        # Provide specific reason for incompatibility
        missing = []
        if not has_mt_slot:
            missing.append("ABS_MT_SLOT")
        if not has_mt_tracking:
            missing.append("ABS_MT_TRACKING_ID")
        if not has_position:
            missing.append("position axes (ABS_MT_POSITION_X/Y or ABS_X/Y)")
        
        reason = f"Missing capabilities: {', '.join(missing)}"
        return False, reason
    
    def check_permissions(self, device_path: str) -> Tuple[bool, str]:
        """Check if we have read permissions for the device."""
        try:
            # Try to open the device
            device = InputDevice(device_path)
            _ = device.capabilities()  # Try to read capabilities
            return True, "Readable"
        except PermissionError:
            return False, "Permission denied (try sudo or add user to 'input' group)"
        except OSError as e:
            return False, f"OS Error: {e}"
    
    def get_device_info(self, device_path: str) -> Optional[Dict]:
        """Get detailed information about a device."""
        try:
            device = InputDevice(device_path)
            is_compatible, reason = self.is_touchpad(device)
            has_permission, perm_reason = self.check_permissions(device_path)
            
            # Get device capabilities details
            try:
                capabilities = device.capabilities()
                has_abs = ecodes.EV_ABS in capabilities
                
                abs_info = {}
                if has_abs:
                    abs_caps = capabilities[ecodes.EV_ABS]
                    for cap in abs_caps:
                        cap_code = cap[0] if isinstance(cap, tuple) else cap
                        cap_name = ecodes.ABS[cap_code] if cap_code in ecodes.ABS else f"Unknown({cap_code})"
                        abs_info[cap_name] = cap_code
            except Exception:
                abs_info = {}
            
            info = {
                'path': device_path,
                'name': device.name,
                'phys': device.phys,
                'info': device.info,
                'is_compatible': is_compatible,
                'compatibility_reason': reason,
                'has_permission': has_permission,
                'permission_reason': perm_reason,
                'abs_capabilities': abs_info
            }
            
            return info
        except Exception as e:
            return {
                'path': device_path,
                'name': 'Unknown',
                'error': str(e),
                'is_compatible': False,
                'compatibility_reason': f"Error accessing device: {e}",
                'has_permission': False
            }
    
    def scan_devices(self):
        """Scan all input devices and categorize them."""
        device_paths = list_devices()
        
        for device_path in device_paths:
            info = self.get_device_info(device_path)
            if info:
                if info.get('is_compatible', False):
                    self.compatible_devices.append(info)
                else:
                    self.incompatible_devices.append(info)
    
    def print_results(self):
        """Print scan results in a formatted way."""
        print("=" * 70)
        print("Linux Three-Finger Drag - Hardware Detection")
        print("=" * 70)
        print()
        
        # System information
        print("System Information:")
        print("-" * 70)
        session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP', 'unknown')
        print(f"Session Type: {session_type}")
        print(f"Desktop Environment: {desktop_env}")
        print(f"User: {os.getenv('USER', 'unknown')}")
        print(f"Groups: {subprocess.run(['groups'], capture_output=True, text=True).stdout.strip()}")
        print()
        
        # Compatible devices
        print(f"Compatible Touchpads: {len(self.compatible_devices)}")
        print("-" * 70)
        if self.compatible_devices:
            for i, device in enumerate(self.compatible_devices, 1):
                print(f"\n[{i}] {device['name']}")
                print(f"    Path: {device['path']}")
                print(f"    Physical: {device.get('phys', 'N/A')}")
                print(f"    Status: {device['compatibility_reason']}")
                print(f"    Permissions: {device['permission_reason']}")
                if device.get('abs_capabilities'):
                    relevant_caps = ['ABS_MT_SLOT', 'ABS_MT_TRACKING_ID', 
                                   'ABS_MT_POSITION_X', 'ABS_MT_POSITION_Y', 
                                   'ABS_X', 'ABS_Y']
                    found_caps = [cap for cap in relevant_caps 
                                if any(cap in str(k) for k in device['abs_capabilities'].keys())]
                    if found_caps:
                        print(f"    Key Capabilities: {', '.join(found_caps)}")
        else:
            print("No compatible touchpads found.")
        print()
        
        # Incompatible devices (only show if verbose or if no compatible devices)
        if not self.compatible_devices or '--verbose' in sys.argv or '-v' in sys.argv:
            print(f"Other Input Devices: {len(self.incompatible_devices)}")
            print("-" * 70)
            for device in self.incompatible_devices[:10]:  # Limit to first 10
                print(f"  {device['name']} ({device['path']})")
                if 'error' not in device:
                    print(f"    Reason: {device['compatibility_reason']}")
            if len(self.incompatible_devices) > 10:
                print(f"  ... and {len(self.incompatible_devices) - 10} more")
            print()
        
        # Recommendations
        print("Recommendations:")
        print("-" * 70)
        if not self.compatible_devices:
            print("❌ No compatible touchpads detected.")
            print("   - Make sure you have a multi-touch trackpad")
            print("   - Check that input devices are accessible")
            print("   - Try running with sudo: sudo python3 detect_hardware.py")
        else:
            compatible_with_perms = [d for d in self.compatible_devices if d['has_permission']]
            if compatible_with_perms:
                recommended = compatible_with_perms[0]
                print(f"✅ Recommended device: {recommended['path']}")
                print(f"   Device: {recommended['name']}")
                print()
                print("To use this device, run:")
                print(f"   python3 three_finger_drag.py --device {recommended['path']}")
            else:
                print("⚠️  Compatible touchpads found but permission issues detected.")
                print("   - Add user to 'input' group: sudo usermod -a -G input $USER")
                print("   - Or run with sudo: sudo python3 three_finger_drag.py")
                print("   - Log out and back in after adding to group")
        
        print()
        print("=" * 70)

def main():
    """Main entry point."""
    detector = TouchpadDetector()
    detector.scan_devices()
    detector.print_results()

if __name__ == '__main__':
    main()

