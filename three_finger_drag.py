#!/usr/bin/env python3
"""
Three-Finger Drag for Linux
Implements macOS-style 3-finger drag on Linux trackpads.
"""

import logging
import os
import sys
import time
from enum import Enum
from typing import Dict, Optional, Tuple

try:
    from evdev import InputDevice, ecodes, categorize
    import uinput
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: sudo apt install python3-evdev python3-uinput")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GestureState(Enum):
    """State machine for gesture recognition."""
    IDLE = 0
    THREE_FINGER_DETECTED = 3
    LOCKING_POSITIONS = 4  # Waiting for delay, then lock cursor position
    WAITING_FOR_THRESHOLD = 5
    DRAGGING = 6
    RELEASING = 7  # Waiting for delay, then release click

def check_session_compatibility() -> bool:
    """Check if running on compatible session type."""
    session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown')
    if session_type.lower() != 'x11':
        logger.warning(
            f"Running on {session_type}, but X11 is required. "
            "Switch to X11 for proper functionality."
        )
        return False
    return True

class ThreeFingerDrag:
    """Main class for handling 3-finger drag gestures."""
    
    # ABS event codes
    ABS_MT_SLOT = ecodes.ABS_MT_SLOT
    ABS_MT_TRACKING_ID = ecodes.ABS_MT_TRACKING_ID
    ABS_MT_POSITION_X = ecodes.ABS_MT_POSITION_X
    ABS_MT_POSITION_Y = ecodes.ABS_MT_POSITION_Y
    ABS_X = ecodes.ABS_X
    ABS_Y = ecodes.ABS_Y
    ABS_PRESSURE = ecodes.ABS_PRESSURE
    
    def __init__(self,
                 device_path: Optional[str] = None,
                 threshold: int = 10,
                 drag_sensitivity: float = 1.0,
                 left_handed: bool = False,
                 leading_finger_weight: float = 1.5,
                 other_fingers_weight: float = 0.3):
        """Initialize the 3-finger drag handler."""
        self.device_path = device_path
        self.threshold = threshold
        self.drag_sensitivity = drag_sensitivity
        self.left_handed = left_handed
        self.leading_finger_weight = leading_finger_weight
        self.other_fingers_weight = other_fingers_weight
        
        # Find and open touchpad
        self.device = self._find_touchpad(device_path)
        self.virtual_mouse = self._create_virtual_mouse()
        
        # Setup coordinate scaling
        self._setup_coordinate_scaling()
        
        # State tracking
        self.state = GestureState.IDLE
        self.active_slots: Dict[int, int] = {}  # slot -> tracking_id
        self.slot_positions: Dict[int, Tuple[int, int]] = {}  # slot -> (x, y)
        self.slot_pressures: Dict[int, int] = {}  # slot -> pressure
        self.initial_position: Optional[Tuple[int, int]] = None
        self.last_position: Optional[Tuple[int, int]] = None
        
        # Drag state
        self.is_dragging = False
        self.drag_lock_timer = None
        
        # Cursor locking for relative movement
        self.cursor_lock_position: Optional[Tuple[int, int]] = None
        self.initial_left_finger_position: Optional[Tuple[int, int]] = None
        
        # Micro-delays for stability
        self.detection_delay = 0.05  # 50ms after detection
        self.click_delay = 0.02  # 20ms before click
        self.release_delay = 0.03  # 30ms after lift
        
        # Delay timers
        self.detection_timer: Optional[float] = None
        self.release_timer: Optional[float] = None
        
        logger.info(f"Initialized 3-finger drag on device: {self.device.name}")
    
    def _get_current_cursor_position(self) -> Tuple[int, int]:
        """Get current cursor position using xdotool or X11."""
        # Try xdotool first
        try:
            import subprocess
            result = subprocess.run(
                ['xdotool', 'getmouselocation', '--shell'],
                capture_output=True, text=True, timeout=0.1
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                x_line = [l for l in lines if l.startswith('X=')]
                y_line = [l for l in lines if l.startswith('Y=')]
                if x_line and y_line:
                    x = int(x_line[0].split('=')[1])
                    y = int(y_line[0].split('=')[1])
                    return (x, y)
        except Exception:
            pass
        
        # Try X11 directly
        try:
            from Xlib import display
            d = display.Display()
            root = d.screen().root
            pointer = root.query_pointer()
            return (pointer.root_x, pointer.root_y)
        except ImportError:
            logger.warning("xdotool not installed. Install with: sudo apt install xdotool")
            logger.warning("Or install python3-xlib: sudo apt install python3-xlib")
        except Exception as e:
            logger.debug(f"Could not get cursor position via X11: {e}")
        
        # Last resort: Use relative movement only (don't lock to 0,0)
        # Return None to indicate we can't get position, and handle it differently
        logger.warning("Cannot get cursor position - using relative movement only")
        return None
    
    def _setup_coordinate_scaling(self):
        """Setup coordinate scaling factors."""
        abs_info = self.device.absinfo(self.ABS_MT_POSITION_X)
        self.x_max = abs_info.max if abs_info else 32767
        self.y_max = abs_info.max if abs_info else 32767
    
    def _find_touchpad(self, path: Optional[str] = None) -> InputDevice:
        """Find the touchpad device."""
        if path:
            return InputDevice(path)
        
        # Search for touchpad
        for device_path in ['/dev/input/event14', '/dev/input/event5']:
            try:
                device = InputDevice(device_path)
                if self._is_touchpad(device):
                    return device
            except (OSError, PermissionError):
                continue
        
        # Search all input devices
        for device_path in sorted(os.listdir('/dev/input')):
            if device_path.startswith('event'):
                try:
                    device = InputDevice(f'/dev/input/{device_path}')
                    if self._is_touchpad(device):
                        return device
                except (OSError, PermissionError):
                    continue
        
        raise RuntimeError(
            "Could not find touchpad device. "
            "Make sure you have read permissions (run with sudo or add user to input group)"
        )
    
    def _is_touchpad(self, device: InputDevice) -> bool:
        """Check if device is a touchpad."""
        capabilities = device.capabilities()
        
        if ecodes.EV_ABS not in capabilities:
            return False
        
        abs_caps = [cap[0] if isinstance(cap, tuple) else cap 
                   for cap in capabilities[ecodes.EV_ABS]]
        
        device_name = device.name.lower()
        is_apple_trackpad = 'bcm5974' in device_name or 'apple' in device_name
        
        if is_apple_trackpad and ecodes.EV_ABS in capabilities:
            logger.debug(f"Detected Apple trackpad: {device.name}")
            return True
        
        has_mt_slot = self.ABS_MT_SLOT in abs_caps
        has_mt_tracking = self.ABS_MT_TRACKING_ID in abs_caps
        has_position = (
            self.ABS_MT_POSITION_X in abs_caps or
            self.ABS_X in abs_caps
        )
        
        return has_mt_slot and has_mt_tracking and has_position
    
    def _create_virtual_mouse(self) -> uinput.Device:
        """Create a virtual mouse device."""
        try:
            return uinput.Device([
                uinput.BTN_LEFT,
                uinput.BTN_RIGHT,
                uinput.BTN_MIDDLE,
                uinput.REL_X,
                uinput.REL_Y,
            ])
        except OSError:
            raise RuntimeError(
                "Permission denied: Need write access to /dev/uinput. "
                "Run with sudo or configure udev rules."
            )
    
    def _get_active_finger_count(self) -> int:
        """Count currently active fingers."""
        return sum(1 for tid in self.active_slots.values() if tid >= 0)
    
    def _update_slot(self, slot: int, tracking_id: Optional[int] = None):
        """Update tracking ID for a slot."""
        if tracking_id is not None:
            if tracking_id < 0:
                self.active_slots.pop(slot, None)
                self.slot_positions.pop(slot, None)
                self.slot_pressures.pop(slot, None)
            else:
                self.active_slots[slot] = tracking_id
    
    def _get_leftmost_finger_position(self) -> Optional[Tuple[int, int]]:
        """Get position of leftmost finger."""
        if len(self.slot_positions) < 3:
            return None
        
        active_positions = [
            (slot, pos) for slot, pos in self.slot_positions.items()
            if slot in self.active_slots
        ]
        
        if len(active_positions) < 3:
            return None
        
        sorted_by_x = sorted(active_positions, key=lambda x: x[1][0])
        return sorted_by_x[0][1]
    
    def _get_rightmost_finger_position(self) -> Optional[Tuple[int, int]]:
        """Get position of rightmost finger."""
        if len(self.slot_positions) < 3:
            return None
        
        active_positions = [
            (slot, pos) for slot, pos in self.slot_positions.items()
            if slot in self.active_slots
        ]
        
        if len(active_positions) < 3:
            return None
        
        sorted_by_x = sorted(active_positions, key=lambda x: x[1][0], reverse=True)
        return sorted_by_x[0][1]
    
    def _get_weighted_position(self) -> Optional[Tuple[int, int]]:
        """Get weighted average position, boosting leading finger."""
        if len(self.slot_positions) < 3:
            return None
        
        active_positions = [
            (slot, pos) for slot, pos in self.slot_positions.items()
            if slot in self.active_slots
        ]
        
        if len(active_positions) < 3:
            return None
        
        # Find leading finger (leftmost for right-handed, rightmost for left-handed)
        sorted_by_x = sorted(active_positions, key=lambda x: x[1][0], reverse=self.left_handed)
        leading_slot, leading_pos = sorted_by_x[0]
        
        # Calculate weighted average
        total_x = 0
        total_y = 0
        total_weight = 0
        
        for slot, pos in active_positions:
            if slot == leading_slot:
                weight = self.leading_finger_weight
            else:
                weight = self.other_fingers_weight
            
            total_x += pos[0] * weight
            total_y += pos[1] * weight
            total_weight += weight
        
        if total_weight == 0:
            return None
        
        return (int(total_x / total_weight), int(total_y / total_weight))
    
    def _get_tracking_position(self) -> Optional[Tuple[int, int]]:
        """Get position to track for dragging."""
        return self._get_weighted_position()
    
    def _start_drag(self):
        """Start dragging (press mouse button)."""
        if not self.is_dragging:
            self.virtual_mouse.emit(uinput.BTN_LEFT, 1)
            self.virtual_mouse.syn()
            self.is_dragging = True
            # Initialize last_position for relative movement tracking
            if self.cursor_lock_position is not None:
                self.last_position = self.cursor_lock_position
            elif self.initial_left_finger_position is not None:
                self.last_position = self.initial_left_finger_position
            logger.debug("Drag started")
    
    def _update_drag(self, position: Tuple[int, int]):
        """Update drag position - uses relative movement."""
        if not self.is_dragging:
            return
        
        if self.last_position:
            # Calculate relative movement
            dx = position[0] - self.last_position[0]
            dy = position[1] - self.last_position[1]
            
            if dx != 0 or dy != 0:
                # Emit relative movement
                self.virtual_mouse.emit(uinput.REL_X, dx)
                self.virtual_mouse.emit(uinput.REL_Y, dy)
                self.virtual_mouse.syn()
                logger.debug(f"Drag move: dx={dx}, dy={dy}")
        
        self.last_position = position
    
    def _end_drag(self, immediate: bool = False):
        """End dragging (release mouse button)."""
        if self.is_dragging:
            self.virtual_mouse.emit(uinput.BTN_LEFT, 0)
            self.virtual_mouse.syn()
            self.is_dragging = False
            self.last_position = None
            self.initial_position = None
            logger.debug("Drag ended")
    
    def _process_frame(self):
        """Process a complete event frame."""
        finger_count = self._get_active_finger_count()
        
        if finger_count == 3:
            if self.state == GestureState.IDLE:
                self.state = GestureState.THREE_FINGER_DETECTED
                # Start delay timer
                self.detection_timer = time.time()
            
            elif self.state == GestureState.THREE_FINGER_DETECTED:
                # Check if delay elapsed
                if time.time() - self.detection_timer >= self.detection_delay:
                    # Lock positions
                    cursor_pos = self._get_current_cursor_position()
                    left_finger = self._get_tracking_position()
                    if left_finger:
                        if cursor_pos is not None:
                            self.cursor_lock_position = cursor_pos
                            self.initial_left_finger_position = left_finger
                            self.state = GestureState.LOCKING_POSITIONS
                            logger.debug(f"Locked cursor at {self.cursor_lock_position}, finger at {self.initial_left_finger_position}")
                        else:
                            # Can't get cursor position - use relative movement only
                            self.initial_left_finger_position = left_finger
                            self.last_position = left_finger  # Initialize for relative tracking
                            self.state = GestureState.LOCKING_POSITIONS
                            logger.debug(f"Using relative movement only (cursor position unavailable), finger at {self.initial_left_finger_position}")
            
            elif self.state == GestureState.LOCKING_POSITIONS:
                # Check movement threshold
                current_left = self._get_tracking_position()
                if current_left and self.initial_left_finger_position:
                    dx = abs(current_left[0] - self.initial_left_finger_position[0])
                    dy = abs(current_left[1] - self.initial_left_finger_position[1])
                    if dx > self.threshold or dy > self.threshold:
                        # Small delay before click
                        time.sleep(self.click_delay)
                        self.state = GestureState.DRAGGING
                        self._start_drag()
            
            elif self.state == GestureState.DRAGGING:
                # Track relative movement
                current_left = self._get_tracking_position()
                if current_left and self.initial_left_finger_position:
                    if self.cursor_lock_position is not None:
                        # Calculate offset from initial finger position
                        offset_x = current_left[0] - self.initial_left_finger_position[0]
                        offset_y = current_left[1] - self.initial_left_finger_position[1]
                        
                        # Apply offset to locked cursor position
                        new_x = self.cursor_lock_position[0] + int(offset_x * self.drag_sensitivity)
                        new_y = self.cursor_lock_position[1] + int(offset_y * self.drag_sensitivity)
                        
                        # Move cursor relative to lock position
                        self._update_drag((new_x, new_y))
                    else:
                        # Pure relative movement (cursor position unavailable)
                        # Calculate movement from initial finger position
                        offset_x = current_left[0] - self.initial_left_finger_position[0]
                        offset_y = current_left[1] - self.initial_left_finger_position[1]
                        
                        # Apply sensitivity and emit relative movement directly
                        if offset_x != 0 or offset_y != 0:
                            dx = int(offset_x * self.drag_sensitivity)
                            dy = int(offset_y * self.drag_sensitivity)
                            if dx != 0 or dy != 0:
                                self.virtual_mouse.emit(uinput.REL_X, dx)
                                self.virtual_mouse.emit(uinput.REL_Y, dy)
                                self.virtual_mouse.syn()
                                logger.debug(f"Relative drag move: dx={dx}, dy={dy}")
                            
                            # Update initial position for next frame (to prevent accumulation)
                            # This makes movement relative to the last frame, not the absolute start
                            self.initial_left_finger_position = current_left
        
        elif finger_count == 0 and self.state == GestureState.DRAGGING:
            # Fingers lifted - start release delay
            self.state = GestureState.RELEASING
            self.release_timer = time.time()
        
        elif self.state == GestureState.RELEASING:
            # Check if release delay elapsed
            if time.time() - self.release_timer >= self.release_delay:
                self._end_drag(immediate=True)
                self.state = GestureState.IDLE
                # Reset locks
                self.cursor_lock_position = None
                self.initial_left_finger_position = None
    
    def _process_event(self, event):
        """Process a single input event."""
        if event.type == ecodes.EV_ABS:
            code = event.code
            
            if code == self.ABS_MT_SLOT:
                self.current_slot = event.value
            elif code == self.ABS_MT_TRACKING_ID:
                if self.current_slot is not None:
                    self._update_slot(self.current_slot, event.value)
            elif code == self.ABS_MT_POSITION_X:
                if self.current_slot is not None:
                    if self.current_slot not in self.slot_positions:
                        self.slot_positions[self.current_slot] = (0, 0)
                    x, y = self.slot_positions[self.current_slot]
                    self.slot_positions[self.current_slot] = (event.value, y)
            elif code == self.ABS_MT_POSITION_Y:
                if self.current_slot is not None:
                    if self.current_slot not in self.slot_positions:
                        self.slot_positions[self.current_slot] = (0, 0)
                    x, y = self.slot_positions[self.current_slot]
                    self.slot_positions[self.current_slot] = (x, event.value)
            elif code == self.ABS_PRESSURE:
                if self.current_slot is not None:
                    self.slot_pressures[self.current_slot] = event.value
        
        elif event.type == ecodes.EV_SYN and event.code == ecodes.SYN_REPORT:
            # Complete frame received - process it
            self._process_frame()
    
    def run(self):
        """Main event loop."""
        logger.info("Starting 3-finger drag handler...")
        logger.info("1-2 finger gestures are handled by the system.")
        logger.info("3-finger drag will activate automatically.")
        
        self.current_slot = None
        
        try:
            for event in self.device.read_loop():
                self._process_event(event)
        except KeyboardInterrupt:
            logger.info("Stopped by user")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        finally:
            if self.is_dragging:
                self._end_drag(immediate=True)

def main():
    """Main entry point."""
    import argparse
    
    # Import config module (handle gracefully if not available)
    try:
        import config
    except ImportError:
        config = None
        logger.warning("config module not available, using defaults only")
    
    parser = argparse.ArgumentParser(description='3-Finger Drag for Linux')
    parser.add_argument('--device', help='Touchpad device path')
    parser.add_argument('--threshold', type=int, help='Movement threshold')
    parser.add_argument('--drag-sensitivity', type=float, help='Drag sensitivity')
    parser.add_argument('--left-handed', action='store_true', help='Use rightmost finger for left-handed users')
    parser.add_argument('--leading-weight', type=float, help='Weight for leading finger')
    parser.add_argument('--other-weight', type=float, help='Weight for other fingers')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    base_config = {}
    if config:
        try:
            base_config = config.load_config(args.config)
            logger.debug(f"Loaded config from: {args.config or config.get_config_path()}")
        except config.ConfigError as e:
            logger.warning(f"Config loading error: {e}. Using defaults.")
        except Exception as e:
            logger.warning(f"Unexpected config error: {e}. Using defaults.")
    
    # Build command-line argument config
    cli_config = {}
    if args.device:
        cli_config['device'] = args.device
    if args.threshold is not None:
        cli_config['threshold'] = args.threshold
    if args.drag_sensitivity is not None:
        cli_config['drag_sensitivity'] = args.drag_sensitivity
    if args.left_handed:
        cli_config['left_handed'] = True
    if args.leading_weight is not None:
        cli_config['leading_finger_weight'] = args.leading_weight
    if args.other_weight is not None:
        cli_config['other_fingers_weight'] = args.other_weight
    
    # Merge configs (CLI overrides file config)
    if config:
        try:
            final_config = config.merge_configs(base_config, cli_config)
        except Exception as e:
            logger.warning(f"Config merge error: {e}. Using CLI args with defaults.")
            # Fall back to CLI args with defaults
            final_config = {**config.DEFAULT_CONFIG, **cli_config}
    else:
        # No config module - use defaults with CLI overrides
        final_config = {
            'device': None,
            'threshold': 10,
            'drag_sensitivity': 1.0,
            'left_handed': False,
            'leading_finger_weight': 1.5,
            'other_fingers_weight': 0.3,
            **cli_config
        }
    
    # Extract values (all should have defaults from above)
    device_path = final_config.get('device')
    threshold = final_config.get('threshold', 10)
    drag_sensitivity = final_config.get('drag_sensitivity', 1.0)
    left_handed = final_config.get('left_handed', False)
    leading_finger_weight = final_config.get('leading_finger_weight', 1.5)
    other_fingers_weight = final_config.get('other_fingers_weight', 0.3)
    
    if not check_session_compatibility():
        logger.warning("Continuing anyway, but X11 is recommended.")
    
    try:
        handler = ThreeFingerDrag(
            device_path=device_path,
            threshold=threshold,
            drag_sensitivity=drag_sensitivity,
            left_handed=left_handed,
            leading_finger_weight=leading_finger_weight,
            other_fingers_weight=other_fingers_weight
        )
        handler.run()
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
