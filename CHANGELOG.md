# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2026-02-18

### Fixed
- Fixed `--wayland-helper` flag not displaying TUI
  - Preserved stdin/stdout/stderr in subprocess.run() to maintain TTY connection
  - Wayland helper TUI now properly detects terminal and displays interactive interface
- Fixed GUI not launching from desktop file
  - Fixed path resolution to work correctly when launched as installed entry point
  - Added development mode detection to handle both source and installed package scenarios
  - Improved error handling with visible error dialogs for desktop launches
  - Added DISPLAY environment variable check before GUI initialization
  - Added comprehensive error logging to `~/.config/draggg/gui_error.log`
  - Improved import error messages with installation instructions
  - GUI now shows user-friendly error dialogs instead of silently failing

## [1.0.4] - 2026-02-18

### Fixed
- Fixed wayland-to-x11 commands not being installed
  - Added wayland-to-x11 entry points to `pyproject.toml` `[project.scripts]` section
  - pyproject.toml was overriding setup.py entry points, causing wayland commands to be missing
  - All four commands now properly installed: `draggg`, `draggg-gui`, `wayland-to-x11`, `wayland-to-x11-tui`

## [1.0.3] - 2026-02-18

### Fixed
- Fixed commands not being found after `pip install draggg`
  - Added `recursive-include scripts *.py` to MANIFEST.in to ensure scripts directory is included in package distribution
  - Verified entry points are correctly configured and scripts package is properly installed

## [1.0.2] - 2026-02-18

### Added
- Wayland to X11 conversion helper tools
  - `wayland-to-x11` command-line script for automated conversion
  - `wayland-to-x11-tui` interactive TUI helper with curses interface
  - `draggg --wayland-helper` flag to launch conversion helper
- Automatic display manager detection (GDM, LightDM, SDDM)
- Distribution-aware config file modification for GDM
- Backup creation before config modification
- Integration with Wayland warning system in draggg
- Extended `gui/utils.py` with display manager detection functions

### Changed
- Improved Wayland detection and user guidance
- Enhanced Wayland warning messages to suggest automated conversion helper
- Updated README.md with Wayland to X11 conversion instructions

## [1.0.1] - 2026-02-18

### Fixed
- Fixed `draggg` and `draggg-gui` commands not being available after pip install
  - Added `draggg_gui` to `py_modules` in setup.py to enable entry point
- Fixed broken desktop file icon and executable path
  - Updated desktop file to use `draggg-gui` command instead of placeholder path
  - Fixed icon reference from `Icon=icon` to `Icon=draggg` to match installed icon files
  - Added post-install command to automatically rename icons from `icon*.png` to `draggg.png`
  - Post-install command ensures desktop file has correct icon reference

### Added
- Post-installation verification script (`check_installation.py`) to verify entry points, PATH, desktop file, and icons
- PATH troubleshooting section in README.md with instructions for adding `~/.local/bin` to PATH
- Post-install command in setup.py to automatically fix icon names and desktop file references

### Changed
- Improved installation experience - commands now work immediately after `pip install draggg`
- Icons are automatically renamed during installation to match desktop file expectations

## [1.0.0] - 2026-02-18

### Added
- Initial release of draggg
- macOS-style three-finger drag gesture support for Linux trackpads
- Intelligent weighted finger tracking with leading finger emphasis
- Automatic hardware detection for compatible touchpads
- GUI setup wizard and configuration tool
- Command-line interface with customizable options
- Left-handed mode support
- Configurable drag sensitivity and movement thresholds
- Systemd service support for background operation
- X11 display server compatibility (recommended)
- Wayland support (limited)
- Support for Apple trackpads, Synaptics, and libinput touchpads
- PyPI package distribution
- Snap package support
- Debian package support
- Conda recipe for conda-forge

### Features
- Three-finger drag gesture recognition
- Offset-based cursor movement calculation
- State machine for gesture recognition
- Micro-delays for gesture stability
- Verbose logging for debugging
- Configuration file support
- Desktop entry and application menu integration
- Icon assets in multiple sizes

### Technical Details
- Python 3.8+ requirement
- Dependencies: evdev, python-uinput
- Optional dependencies: pystray, Pillow (for system tray)
- Universal wheel distribution (py3-none-any) for all architectures

[1.0.0]: https://github.com/j031nich0145/draggg/releases/tag/v1.0.0
