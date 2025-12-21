# draggg Packaging and Distribution Protocol

This document outlines the complete protocol for preparing draggg for distribution across multiple package managers and platforms.

## Overview

This protocol covers:
- Icon generation and asset preparation
- Desktop entry and shortcut creation
- Package creation for pip, snap, apt (Debian), and conda
- Final verification and testing procedures
- Documentation updates

---

## Phase 1: Asset Preparation

### 1.1 Icon Generation

**Script:** `create_icon.py`

**Steps:**
1. Ensure Pillow/PIL is installed: `pip install Pillow`
2. Run icon generation:
   ```bash
   python3 create_icon.py
   ```
3. Verify icons created:
   - `assets/icon.png` (256x256) - Main icon
   - `assets/icon-128.png` (128x128)
   - `assets/icon-64.png` (64x64)
   - `assets/icon-48.png` (48x48)

**Verification:**
- All icons exist and have correct dimensions
- Icons display correctly when viewed
- Icons are recognizable and professional

### 1.2 Desktop Entry File

**File:** `draggg.desktop`

**Requirements:**
- Must include: Name, GenericName, Comment, Exec, Icon, Terminal, Categories, Keywords
- Icon path must use placeholder: `/path/to/draggg/assets/icon.png`
- Exec path must use placeholder: `/path/to/draggg/draggg_gui.py`
- Categories: `Settings;System;Accessibility;`
- Keywords: `gesture;touchpad;drag;accessibility;mouse;trackpad;`

**Verification:**
- File validates: `desktop-file-validate draggg.desktop`
- All required fields present
- No syntax errors

---

## Phase 2: Package Configuration Files

### 2.1 Python Package (pip)

**Files:**
- `setup.py`
- `MANIFEST.in`

**Checklist:**
- [ ] `setup.py` includes all required metadata
- [ ] Entry points configured: `draggg` and `draggg-gui`
- [ ] Package data includes icons and desktop entry
- [ ] Dependencies listed in `install_requires`
- [ ] `MANIFEST.in` includes all necessary files

**Test Build:**
```bash
python3 setup.py sdist bdist_wheel
ls -lh dist/
```

**Test Install:**
```bash
pip install dist/draggg-*.whl
which draggg
which draggg-gui
draggg --help
draggg-gui
```

### 2.2 Snap Package

**File:** `snap/snapcraft.yaml`

**Checklist:**
- [ ] Name, version, summary, description set
- [ ] Base and confinement level appropriate
- [ ] Apps defined: draggg, draggg-gui, draggg-service
- [ ] Plugs configured (hardware-observer, x11, desktop)
- [ ] Python plugin configured
- [ ] Requirements file referenced
- [ ] Desktop entry organized correctly

**Test Build:**
```bash
snapcraft
snap list | grep draggg
```

**Test Install:**
```bash
sudo snap install draggg_*.snap --dangerous
snap run draggg --help
snap run draggg-gui
```

### 2.3 Debian Package

**Files:**
- `debian/control`
- `debian/rules`
- `debian/changelog`
- `debian/compat`
- `debian/install`

**Checklist:**
- [ ] `control` has proper metadata and dependencies
- [ ] `rules` installs icons to correct locations
- [ ] `changelog` updated with version and changes
- [ ] `compat` set to appropriate version
- [ ] `install` maps files correctly

**Test Build:**
```bash
dpkg-buildpackage -b
ls -lh ../draggg_*.deb
```

**Test Install:**
```bash
sudo dpkg -i ../draggg_*.deb
# Check for missing dependencies
sudo apt-get install -f
```

### 2.4 Conda Package

**File:** `conda/meta.yaml`

**Checklist:**
- [ ] Name, version, and build number set
- [ ] Source path correct
- [ ] Build script uses pip install
- [ ] Entry points defined
- [ ] Dependencies listed (build, host, run)
- [ ] Test imports specified

**Test Build:**
```bash
conda build conda/
conda install --use-local draggg
draggg --help
```

---

## Phase 3: Setup Script and GUI Integration

### 3.1 Setup Script Shortcut Options

**File:** `setup.sh`

**Function:** `install_desktop_entry()`

**Checklist:**
- [ ] Function accepts parameters: `install_desktop_entry <app_menu> <desktop_shortcut>`
- [ ] Application menu entry created in `~/.local/share/applications/`
- [ ] Desktop shortcut created in Desktop folder (handles localized names)
- [ ] Paths updated correctly (SCRIPT_DIR substitution)
- [ ] Icon path updated if icon exists
- [ ] Desktop database updated

**Test:**
```bash
./setup.sh
# When prompted, test both options:
# - Create application menu entry: Yes
# - Create desktop shortcut: Yes
# Verify files created and paths correct
```

### 3.2 GUI Wizard Shortcut Options

**File:** `gui/setup_wizard.py`

**Methods:**
- `step_service()` - Add shortcut checkboxes
- `_install_desktop_entry()` - Install shortcuts

**Checklist:**
- [ ] Checkboxes added in final step for:
  - Create application menu entry (default: checked)
  - Create desktop shortcut (default: unchecked)
- [ ] `_install_desktop_entry()` method implemented
- [ ] Paths updated correctly
- [ ] Handles missing desktop directory gracefully

**Test:**
```bash
python3 draggg_gui.py
# Complete setup wizard
# Check both shortcut options
# Verify shortcuts created correctly
```

---

## Phase 4: Configuration and Wiring Verification

### 4.1 GUI Settings Wiring Test

**Purpose:** Verify all GUI sliders and settings properly save to config and are loaded by backend.

**Test Procedure:**

1. **Settings Panel Load Test:**
   ```bash
   # Ensure config exists
   python3 draggg_gui.py
   # Modify all settings:
   # - Threshold slider
   # - Sensitivity slider
   # - Left-handed checkbox
   # - Leading finger weight
   # - Other fingers weight
   # Click "Save Settings"
   ```

2. **Verify Config File:**
   ```bash
   cat ~/.config/three-finger-drag/config.json
   # Verify all values match what was set in GUI
   ```

3. **Backend Load Test:**
   ```bash
   # Stop service if running
   systemctl --user stop draggg.service
   # Start draggg with config
   python3 draggg.py --config ~/.config/three-finger-drag/config.json --verbose
   # Check logs for loaded config values
   # Verify values match what was set in GUI
   ```

4. **Service Integration Test:**
   ```bash
   # Save settings in GUI
   # Restart service from GUI
   # Verify service starts with new settings
   systemctl --user status draggg.service
   journalctl --user -u draggg.service -n 20
   ```

### 4.2 Setup Wizard Configuration Test

**Test Procedure:**

1. **Fresh Setup:**
   ```bash
   # Backup existing config
   mv ~/.config/three-finger-drag/config.json ~/.config/three-finger-drag/config.json.backup
   # Run GUI (should show wizard)
   python3 draggg_gui.py
   # Complete wizard with custom values
   # Verify config saved correctly
   cat ~/.config/three-finger-drag/config.json
   ```

2. **Existing Config:**
   ```bash
   # Restore config
   mv ~/.config/three-finger-drag/config.json.backup ~/.config/three-finger-drag/config.json
   # Run GUI (should show settings panel, not wizard)
   python3 draggg_gui.py
   # Verify settings loaded correctly from config
   ```

### 4.3 Icon Display Test

**Test Procedure:**

1. **Desktop Entry Icon:**
   ```bash
   # Install desktop entry
   ./setup.sh
   # Or manually:
   cp draggg.desktop ~/.local/share/applications/
   # Update paths in file
   update-desktop-database ~/.local/share/applications
   # Search for "draggg" in application menu
   # Verify icon displays correctly
   ```

2. **Desktop Shortcut Icon:**
   ```bash
   # Create desktop shortcut
   cp draggg.desktop ~/Desktop/draggg.desktop
   # Update paths and make executable
   chmod +x ~/Desktop/draggg.desktop
   # Verify icon displays on desktop
   ```

3. **GUI Icon:**
   ```bash
   # Launch GUI
   python3 draggg_gui.py
   # Check window icon (if implemented)
   # Check application menu icon
   ```

---

## Phase 5: Documentation Updates

### 5.1 README Updates

**Section:** "Installation"

**Checklist:**
- [ ] Installation methods listed:
  - pip install
  - snap install
  - apt install (when published)
  - conda install
- [ ] Commands are accurate and tested
- [ ] Links to app stores included (when available)

**Section:** "Packaging and Distribution"

**Checklist:**
- [ ] Build instructions for each package type
- [ ] Test commands included
- [ ] Shortcut creation instructions
- [ ] Development setup instructions

### 5.2 Package-Specific Documentation

**For Each Package Type:**

1. **pip:**
   - Installation from PyPI
   - Installation from source
   - Entry points usage

2. **snap:**
   - Installation from snap store
   - Local installation
   - Permissions and confinement

3. **apt:**
   - Repository setup (when available)
   - Installation from .deb file
   - Dependency resolution

4. **conda:**
   - Installation from conda-forge (when available)
   - Local build and install
   - Environment setup

---

## Phase 6: Final Verification Checklist

### 6.1 Pre-Release Checklist

**Assets:**
- [ ] All icon files exist and are correct size
- [ ] Icons display properly in file manager
- [ ] Desktop entry file validates
- [ ] Desktop entry icon path correct

**Packaging:**
- [ ] All package config files present
- [ ] Version numbers consistent across all packages
- [ ] Dependencies correctly specified
- [ ] Entry points work correctly

**Functionality:**
- [ ] GUI launches from application menu
- [ ] GUI launches from desktop shortcut
- [ ] GUI launches from command line
- [ ] Settings save and load correctly
- [ ] Service starts with correct config
- [ ] All shortcuts work correctly

**Documentation:**
- [ ] README updated with installation methods
- [ ] Packaging instructions included
- [ ] Test procedures documented
- [ ] Troubleshooting section updated

### 6.2 Package Build Verification

**For Each Package Type:**

1. **pip:**
   ```bash
   python3 setup.py sdist bdist_wheel
   pip install dist/draggg-*.whl --force-reinstall
   draggg --help
   draggg-gui
   ```

2. **snap:**
   ```bash
   snapcraft clean
   snapcraft
   sudo snap install draggg_*.snap --dangerous
   snap run draggg --help
   ```

3. **debian:**
   ```bash
   dpkg-buildpackage -b
   sudo dpkg -i ../draggg_*.deb
   sudo apt-get install -f
   draggg --help
   ```

4. **conda:**
   ```bash
   conda build conda/ --no-test
   conda install --use-local draggg
   draggg --help
   ```

### 6.3 Integration Testing

**Full Workflow Test:**

1. **Fresh Install:**
   ```bash
   # Clean environment
   # Install package (choose method)
   # Run setup/configuration
   # Verify all features work
   ```

2. **Update Test:**
   ```bash
   # Existing installation
   # Update package
   # Verify config preserved
   # Verify service restarts correctly
   ```

3. **Uninstall Test:**
   ```bash
   # Uninstall package
   # Verify files removed (except user config)
   # Verify service stopped
   # Verify shortcuts removed
   ```

---

## Phase 8: Development Testing and Bug Fixes

### 8.1 Service File Validation Fixes

**Issue Identified:** Service files generated from template contained invalid `User=%i` directive, causing "bad unit file setting" errors.

**Fixes Applied:**

1. **Template File (`draggg.service`):**
   - Removed `User=%i` line (invalid for user services)
   - Removed comment about changing paths
   - Cleaned up security directives that caused issues
   - Simplified to valid user service format

2. **GUI Setup Wizard (`gui/setup_wizard.py`):**
   - Updated `_install_service_file()` method
   - Added automatic removal of invalid directives when reading template
   - Removes `User=` lines, comments, and cleans formatting
   - Ensures generated service files are always valid

3. **Setup Script (`setup.sh`):**
   - Already creates valid service files (no template dependency)
   - No changes needed

**Test Procedure:**
```bash
# Test service installation via GUI
python3 draggg_gui.py
# Complete setup wizard
# Click "Install Service" button
# Verify service installs without errors

# Verify service file is valid
cat ~/.config/systemd/user/draggg.service
systemctl --user daemon-reload
systemctl --user start draggg.service
systemctl --user status draggg.service
# Should show "active (running)" with no errors
```

### 8.2 Icon Installation Improvements

**Issue Identified:** Icons were only being installed in 256x256 and 128x128 sizes, missing smaller sizes needed for toolbars and application menus.

**Fixes Applied:**

1. **GUI Setup Wizard (`gui/setup_wizard.py`):**
   - Updated `_install_desktop_entry()` method
   - Now installs all icon sizes: 256x256, 128x128, 64x64, 48x48, 32x32, 24x24, 22x22, 16x16
   - Uses 48x48 icon as fallback for smaller toolbar sizes
   - Improved icon cache update with `-f -t` flags
   - Better error handling and reporting

2. **Setup Script (`setup.sh`):**
   - Updated `install_desktop_entry()` function
   - Installs all required icon sizes
   - Proper fallback logic for missing icon files

3. **Manual Fix Script (`fix_icons.sh`):**
   - Created helper script for manual icon installation
   - Can be run independently to fix missing icons
   - Provides verification output

**Test Procedure:**
```bash
# Test icon installation via GUI
python3 draggg_gui.py
# Complete setup wizard
# Check "Create application menu entry"
# Verify all icon sizes installed:

ls -la ~/.local/share/icons/hicolor/*/apps/draggg.png
# Should show: 16x16, 22x22, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256

# Verify icons appear in application menu
# Search for "draggg" - icon should be visible
```

### 8.3 Optional Dependency Handling

**Issue Identified:** pystray was being treated as a required dependency, causing setup warnings.

**Fixes Applied:**

1. **Setup Script (`setup.sh`):**
   - Updated `check_pip_packages()` to skip optional packages (pystray, Pillow)
   - Added informational message that pystray is optional
   - Only warns about truly required dependencies

2. **Requirements File (`requirements.txt`):**
   - Clearly marked pystray and Pillow as optional
   - Added comments explaining they're only needed for --tray flag

3. **Main Script (`draggg.py`):**
   - Improved error handling for missing pystray
   - Better log messages explaining it's optional
   - Service continues running normally without tray icon

**Test Procedure:**
```bash
# Test without pystray installed
pip uninstall -y pystray Pillow
./setup.sh
# Should not complain about missing pystray
# Should note it's optional

# Service should still start
systemctl --user start draggg.service
journalctl --user -u draggg.service -n 20
# Should show warning but service runs normally
```

### 8.4 GUI Service Management Improvements

**Fixes Applied:**

1. **Settings Panel (`gui/settings_panel.py`):**
   - Enhanced all service button handlers with proper error handling
   - Added timeout handling (10 seconds)
   - Improved error messages with stderr/stdout capture
   - Added FileNotFoundError handling for missing systemctl
   - Status refresh after all operations
   - Better exception messages

2. **Uninstall Functionality:**
   - Added comprehensive uninstall feature to Settings Panel
   - Removes service, desktop entries, shortcuts, icons
   - Optional config file removal
   - Updates icon cache and desktop database
   - Shows confirmation dialog with checklist

**Test Procedure:**
```bash
# Test service management buttons
python3 draggg_gui.py
# Go to Service tab
# Test: Start, Stop, Restart, Enable, Disable buttons
# Verify error messages are clear and helpful
# Verify status updates after operations

# Test uninstall
python3 draggg_gui.py
# Go to About tab
# Click "Uninstall draggg"
# Verify removal of all components
# Verify icons/entries removed from system
```

### 8.5 Final Setup Verification

**Complete End-to-End Test:**

1. **Fresh Installation Test:**
   ```bash
   # Remove all traces of previous installation
   rm -rf ~/.config/three-finger-drag
   systemctl --user stop draggg.service 2>/dev/null
   systemctl --user disable draggg.service 2>/dev/null
   rm ~/.config/systemd/user/draggg.service 2>/dev/null
   rm ~/.local/share/applications/draggg.desktop 2>/dev/null
   rm -rf ~/.local/share/icons/hicolor/*/apps/draggg.png
   
   # Run GUI setup wizard
   python3 draggg_gui.py
   # Complete all steps
   # Check "Create application menu entry"
   # Check "Create desktop shortcut"
   # Install service and enable it
   
   # Verify everything works
   systemctl --user status draggg.service
   ls ~/.local/share/applications/draggg.desktop
   ls ~/.local/share/icons/hicolor/*/apps/draggg.png
   ```

2. **Package Installation Test (After Package Build):**
   ```bash
   # For pip:
   pip uninstall draggg -y
   pip install dist/draggg-*.whl
   draggg-gui  # Should launch GUI setup wizard
   
   # For snap:
   sudo snap remove draggg
   sudo snap install draggg_*.snap --dangerous
   snap run draggg-gui
   
   # For apt:
   sudo apt remove draggg
   sudo dpkg -i ../draggg_*.deb
   draggg-gui
   ```

**Verification Checklist:**
- [ ] GUI setup wizard launches correctly
- [ ] All wizard steps work (Welcome, Dependencies, Permissions, Hardware, Configuration, Service)
- [ ] Service installs without errors
- [ ] Service starts successfully
- [ ] All icon sizes installed correctly
- [ ] Desktop entry created and icon appears in application menu
- [ ] Desktop shortcut created (if requested)
- [ ] Settings save and load correctly
- [ ] Service management buttons work (Start, Stop, Restart, Enable, Disable)
- [ ] Uninstall removes all components correctly

---

## Phase 7: Release Preparation

### 7.1 Version Management

**Version Consistency:**
- [ ] Version matches in:
  - `setup.py`
  - `snap/snapcraft.yaml`
  - `debian/changelog`
  - `conda/meta.yaml`
  - `README.md` (if mentioned)

### 7.2 Release Notes

**Document:**
- New features
- Bug fixes
- Breaking changes
- Migration notes
- Known issues

### 7.3 Distribution Channels

**Prepare for:**
- [ ] PyPI upload (pip)
- [ ] Snap Store submission (snap)
- [ ] Debian repository (apt)
- [ ] Conda-forge submission (conda)
- [ ] GitHub releases

---

## Quick Reference Commands

### Icon Generation
```bash
python3 create_icon.py
```

### Package Builds
```bash
# pip
python3 setup.py sdist bdist_wheel

# snap
snapcraft

# debian
dpkg-buildpackage -b

# conda
conda build conda/
```

### Testing
```bash
# GUI launch
python3 draggg_gui.py

# Service management
systemctl --user start draggg.service
systemctl --user status draggg.service
journalctl --user -u draggg.service -f

# Config verification
cat ~/.config/three-finger-drag/config.json
python3 draggg.py --config ~/.config/three-finger-drag/config.json --verbose
```

### Shortcut Creation
```bash
# Via setup script
./setup.sh

# Via GUI
python3 draggg_gui.py

# Manual
cp draggg.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications
```

---

## Troubleshooting

### Common Issues

**Icons not displaying:**
- Verify icon files exist
- Check desktop entry Icon path
- Run `update-desktop-database`
- Check icon theme cache

**Shortcuts not working:**
- Verify paths in desktop file
- Check file permissions (must be executable)
- Verify Python path in Exec line
- Check desktop database updated

**Package build fails:**
- Verify all dependencies installed
- Check for syntax errors in config files
- Verify file paths are correct
- Check build environment matches requirements

**GUI settings not saving:**
- Check config directory permissions
- Verify config file is writable
- Check for errors in GUI console
- Verify config.py save function works

---

## Maintenance Notes

### Regular Updates

**When updating version:**
1. Update version in all package config files
2. Update changelog
3. Update README if needed
4. Rebuild all packages
5. Test each package type
6. Update release notes

**When adding features:**
1. Update package dependencies if needed
2. Update entry points if new commands added
3. Update documentation
4. Test all package types
5. Update changelog

**When fixing bugs:**
1. Document fix in changelog
2. Test fix in all package types
3. Verify no regressions
4. Update known issues if applicable

---

*Last Updated: 2024-12-20*
*Protocol Version: 1.0*

