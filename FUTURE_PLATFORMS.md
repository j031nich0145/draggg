# Multi-Platform Support Roadmap for draggg

## Overview

This document outlines the roadmap for extending draggg to support macOS and Windows platforms, maintaining a single codebase with platform abstraction layers.

## Architecture Design

### Platform Abstraction Layer

Create a platform-agnostic interface that abstracts:
- Touchpad input detection and reading
- Virtual mouse/cursor control
- Cursor position queries
- Permission/access management

### Proposed Structure

```
draggg/
├── draggg/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── gesture_engine.py      # Platform-agnostic gesture recognition
│   │   ├── state_machine.py       # Gesture state management
│   │   └── finger_tracking.py     # Weighted finger position calculation
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract base classes
│   │   ├── linux.py               # Linux implementation (refactor current code)
│   │   ├── macos.py               # macOS implementation
│   │   └── windows.py             # Windows implementation
│   └── main.py                    # Entry point with platform detection
├── draggg.py                      # Legacy entry point (deprecated)
└── ...
```

### Abstract Base Classes

**`platforms/base.py`** will define:

```python
class TouchpadInput(ABC):
    @abstractmethod
    def find_touchpad(self) -> Optional[str]: pass
    @abstractmethod
    def read_events(self) -> Iterator[TouchEvent]: pass
    @abstractmethod
    def get_finger_count(self) -> int: pass
    @abstractmethod
    def get_finger_positions(self) -> List[Tuple[int, int]]: pass

class MouseOutput(ABC):
    @abstractmethod
    def get_cursor_position(self) -> Tuple[int, int]: pass
    @abstractmethod
    def move_cursor(self, dx: int, dy: int): pass
    @abstractmethod
    def press_button(self, button: str): pass
    @abstractmethod
    def release_button(self, button: str): pass
```

## macOS Implementation (Priority 1)

### Requirements

**APIs and Frameworks:**
- **Quartz Event Services** (CoreGraphics) - For reading touchpad events
- **CGEvent** - For simulating mouse events
- **IOKit** - For low-level device access (if needed)
- **PyObjC** - Python bindings for Objective-C/Cocoa APIs

**Dependencies:**
- Python 3.8+
- PyObjC (`pip install pyobjc-framework-Quartz pyobjc-framework-ApplicationServices`)
- macOS 10.9+ (for CGEvent APIs)

**Permissions:**
- Accessibility permissions (System Preferences > Security & Privacy > Accessibility)
- Input monitoring permissions (macOS 10.15+)

### Implementation Approach

**1. Touchpad Input (`platforms/macos.py`):**

```python
from Quartz import (
    CGEventSourceCreate, CGEventSourceGetSourceStateID,
    CGEventTapCreate, kCGEventTapOptionDefault,
    kCGEventMaskForAllEvents, CGEventTapEnable
)
```

- Use **CGEventTap** to intercept touchpad events
- Filter for multi-touch events (NSEvent type)
- Extract finger positions from touch data
- Map to internal finger tracking format

**2. Mouse Output (`platforms/macos.py`):**

```python
from Quartz import (
    CGEventCreateMouseEvent, kCGEventMouseMoved,
    kCGEventLeftMouseDown, kCGEventLeftMouseUp,
    kCGMouseButtonLeft, kCGHIDEventTap
)
```

- Use **CGEventCreateMouseEvent** for cursor movement
- Use **CGEventPost** to inject mouse events
- Handle button press/release events

**3. Cursor Position:**

```python
from Quartz import CGEventGetLocation
```

- Use **CGEventGetLocation** for current cursor position
- More reliable than Linux's xdotool approach

### Challenges

1. **macOS Security Model:**
   - Requires user to grant accessibility permissions
   - May require code signing for distribution
   - Input monitoring requires explicit user consent

2. **Event Tap Limitations:**
   - Event taps can be disabled by system
   - Need to handle tap failures gracefully
   - May need to re-enable tap on system events

3. **Multi-touch Data Format:**
   - macOS uses NSTouch API (Objective-C)
   - Need to bridge to Python via PyObjC
   - Touch data structure differs from Linux evdev

### Testing Requirements

- Test on macOS 10.9 through latest version
- Test with built-in trackpads (MacBook Pro, Air)
- Test with external Magic Trackpad
- Verify permission prompts work correctly
- Test gesture recognition accuracy

## Windows Implementation (Priority 2)

### Requirements

**APIs and Libraries:**
- **Windows Raw Input API** - For reading touchpad events
- **SendInput API** - For simulating mouse events
- **GetCursorPos** - For cursor position queries
- **ctypes** - For calling Windows APIs from Python
- **pywin32** (optional) - Python Windows extensions

**Dependencies:**
- Python 3.8+
- Windows 7+ (for Raw Input API)
- `pywin32` package (`pip install pywin32`) - Optional but recommended

**Permissions:**
- Administrator privileges (may be required for some input methods)
- UAC elevation for device access

### Implementation Approach

**1. Touchpad Input (`platforms/windows.py`):**

```python
from ctypes import windll, Structure, POINTER, byref
from ctypes.wintypes import DWORD, USHORT, UINT

# Windows Raw Input API
RegisterRawInputDevices = windll.user32.RegisterRawInputDevices
GetRawInputData = windll.user32.GetRawInputData
```

- Use **RegisterRawInputDevices** to register for touchpad input
- Use **GetRawInputData** to read touch events
- Parse **RID_DEVICE_INFO_MOUSE** structures
- Extract multi-touch data (Windows 8+ supports multi-touch)

**2. Mouse Output (`platforms/windows.py`):**

```python
from ctypes import windll, Structure
import ctypes

# SendInput API
SendInput = windll.user32.SendInput
```

- Use **SendInput** API for mouse movement and clicks
- Create **INPUT** structures for mouse events
- Handle relative and absolute movement modes

**3. Cursor Position:**

```python
from ctypes import windll, POINTER, byref
from ctypes.wintypes import POINT

GetCursorPos = windll.user32.GetCursorPos
```

- Use **GetCursorPos** for current cursor position
- More straightforward than Linux approach

### Challenges

1. **Windows Touchpad Diversity:**
   - Many different touchpad drivers (Synaptics, Precision, Elan, etc.)
   - Inconsistent multi-touch support
   - May need driver-specific handling

2. **Raw Input API Complexity:**
   - More complex than Linux evdev
   - Requires careful structure definitions
   - Multi-touch support varies by Windows version

3. **Administrator Requirements:**
   - Some input methods require elevated privileges
   - UAC prompts may interrupt user experience
   - Need to handle permission errors gracefully

4. **Windows 8+ Multi-touch:**
   - Better multi-touch support in Windows 8+
   - May need different approaches for Windows 7 vs 8+

### Testing Requirements

- Test on Windows 7, 8, 10, 11
- Test with various touchpad drivers
- Test with built-in laptop trackpads
- Test with external touchpads
- Verify UAC/permission handling
- Test gesture recognition across different hardware

## Implementation Phases

### Phase 1: Refactor Linux Code (Foundation)
- Extract core gesture logic into `core/` modules
- Create platform abstraction interfaces
- Move Linux-specific code to `platforms/linux.py`
- Update main entry point to use platform detection
- **Files to modify:**
  - `draggg.py` → Split into `core/` and `platforms/linux.py`
  - Create `platforms/base.py` with abstract classes
  - Create `main.py` with platform detection

### Phase 2: macOS Implementation
- Implement `platforms/macos.py` with Quartz APIs
- Create macOS-specific setup/installation script
- Add permission request handling
- Test on various macOS versions
- **New files:**
  - `platforms/macos.py`
  - `setup_macos.sh` (or update existing setup.sh)
  - `docs/macos_setup.md`

### Phase 3: Windows Implementation
- Implement `platforms/windows.py` with Windows APIs
- Create Windows-specific installation guide
- Handle UAC/permission requirements
- Test on various Windows versions and hardware
- **New files:**
  - `platforms/windows.py`
  - `setup_windows.bat` or PowerShell script
  - `docs/windows_setup.md`

### Phase 4: Cross-Platform Testing & Polish
- Unified configuration system
- Cross-platform documentation
- CI/CD for all platforms
- Performance optimization

## Contributor Guidelines

### Getting Started

1. **Fork the repository**
2. **Set up development environment:**
   ```bash
   git clone <your-fork>
   cd draggg
   python3 -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   ```

3. **Choose a platform to work on:**
   - Check existing issues for platform-specific tasks
   - Start with macOS if you have a Mac
   - Start with Windows if you have Windows

### Code Structure

- **Core logic** (platform-agnostic) goes in `draggg/core/`
- **Platform-specific code** goes in `draggg/platforms/`
- **Tests** should be in `tests/` with platform-specific test files
- **Documentation** updates go in `docs/` or README

### Coding Standards

- Follow existing code style (PEP 8)
- Add type hints for all functions
- Include docstrings for all classes/functions
- Write unit tests for new features
- Update documentation for API changes

### Testing Requirements

- Test on target platform before submitting PR
- Include test results in PR description
- Test edge cases (permission denied, device not found, etc.)
- Verify gesture recognition accuracy

### Pull Request Process

1. Create a feature branch: `git checkout -b feature/macos-support`
2. Make changes following coding standards
3. Add/update tests
4. Update documentation
5. Submit PR with:
   - Clear description of changes
   - Platform tested on
   - Screenshots/videos if UI changes
   - Test results

### Platform-Specific Contribution Areas

**macOS:**
- Quartz Event Tap implementation
- Permission handling
- Multi-touch data parsing
- CGEvent mouse simulation
- Setup script for macOS

**Windows:**
- Raw Input API implementation
- SendInput mouse simulation
- Multi-touch support detection
- UAC/permission handling
- Windows installer/script

**Both:**
- Core gesture algorithm improvements
- Configuration system
- Documentation
- Testing infrastructure

## Dependencies by Platform

### Linux (Current)
- `python3-evdev` or `evdev` (pip)
- `python3-uinput` or `python-uinput` (pip)
- `xdotool` (system package)
- `python3-xlib` (optional)

### macOS (Future)
- `pyobjc-framework-Quartz` (pip)
- `pyobjc-framework-ApplicationServices` (pip)
- macOS 10.9+ system requirements

### Windows (Future)
- `pywin32` (pip, optional but recommended)
- `ctypes` (built-in)
- Windows 7+ system requirements

## Documentation Updates Needed

1. **README.md:**
   - Add platform support matrix
   - Update installation instructions per platform
   - Add platform-specific troubleshooting

2. **New files:**
   - `CONTRIBUTING.md` - Contributor guidelines (reference this roadmap)
   - `docs/macos_setup.md` - macOS installation guide
   - `docs/windows_setup.md` - Windows installation guide
   - `docs/architecture.md` - Architecture overview

## Success Criteria

**macOS:**
- [ ] Three-finger drag works on macOS 10.9+
- [ ] Permission prompts work correctly
- [ ] Gesture recognition matches Linux accuracy
- [ ] Setup script handles macOS dependencies
- [ ] Documentation complete

**Windows:**
- [ ] Three-finger drag works on Windows 7+
- [ ] Works with major touchpad drivers
- [ ] UAC/permission handling works
- [ ] Setup process documented
- [ ] Documentation complete

**Both:**
- [ ] Single codebase maintained
- [ ] Platform abstraction working
- [ ] Tests passing on all platforms
- [ ] CI/CD setup for all platforms

## Questions for Contributors

If you're interested in contributing, consider:
- Which platform do you have access to?
- Are you familiar with platform-specific APIs?
- Can you test on multiple hardware configurations?
- Are you interested in core algorithm improvements?

## Next Steps

1. **Immediate:** Create platform abstraction layer (Phase 1)
2. **Short-term:** Implement macOS support (Phase 2)
3. **Medium-term:** Implement Windows support (Phase 3)
4. **Long-term:** Cross-platform polish and optimization (Phase 4)

For questions or to claim a task, open an issue or start a discussion in the repository.

