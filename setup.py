#!/usr/bin/env python3
"""
Setup script for draggg - Three-Finger Drag for Linux
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import os
import shutil
import sys

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse requirement (handle comments after package name)
                req = line.split('#')[0].strip()
                if req:
                    requirements.append(req)


class PostInstallCommand(install):
    """Post-installation command to rename icons and fix desktop file."""
    
    def run(self):
        install.run(self)
        # Run post-install tasks after installation completes
        try:
            self.rename_icons()
            self.fix_desktop_file()
            # Install user files (desktop entry and icons) for --user installations
            self.install_user_files()
        except Exception as e:
            # Don't fail installation if post-install tasks fail
            pass  # Silent - don't print warnings during pip install
        
        # Print a clear post-install message so the user knows what to do next
        self._print_postinstall_message()
    
    def _print_postinstall_message(self):
        """Print a visible post-install message directing the user to run draggg-setup."""
        print()
        print("=" * 60)
        print("  draggg installed successfully!")
        print()
        print("  To complete setup, open a terminal and run:")
        print()
        print("      draggg-setup")
        print()
        print("  This will:")
        print("    - Set up input device permissions")
        print("    - Install and enable the background service")
        print("    - Launch the GUI to configure settings")
        print()
        print("  If 'draggg-setup' is not found, add ~/.local/bin to")
        print("  your PATH or run:")
        print()
        print("      python -m scripts.post_install_setup")
        print("=" * 60)
        print()
    
    def rename_icons(self):
        """Rename installed icons from icon*.png to draggg.png"""
        import site
        
        # Check both user and system installation locations
        prefixes = []
        
        # User installation
        try:
            user_base = Path(site.getuserbase())
            if user_base.exists():
                prefixes.append(user_base)
        except:
            pass
        
        # System installation (check common locations)
        if hasattr(self, 'install_base') and self.install_base:
            prefixes.append(Path(self.install_base))
        else:
            # Try common system locations
            for sys_prefix in ["/usr/local", "/usr"]:
                if Path(sys_prefix).exists():
                    prefixes.append(Path(sys_prefix))
        
        icon_sizes_map = {
            "256x256": "icon.png",
            "128x128": "icon-128.png",
            "64x64": "icon-64.png",
            "48x48": "icon-48.png",
        }
        
        renamed_count = 0
        for prefix in prefixes:
            icon_base = prefix / "share" / "icons" / "hicolor"
            
            for size, old_filename in icon_sizes_map.items():
                icon_dir = icon_base / size / "apps"
                old_name = icon_dir / old_filename
                new_name = icon_dir / "draggg.png"
                
                if old_name.exists() and not new_name.exists():
                    try:
                        icon_dir.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(old_name), str(new_name))
                        renamed_count += 1
                    except Exception as e:
                        pass  # Silently continue
    
    def fix_desktop_file(self):
        """Ensure desktop file has correct icon reference"""
        import site
        import re
        
        # Check both user and system installation locations
        prefixes = []
        
        # User installation
        try:
            user_base = Path(site.getuserbase())
            if user_base.exists():
                prefixes.append(user_base)
        except:
            pass
        
        # System installation
        if hasattr(self, 'install_base') and self.install_base:
            prefixes.append(Path(self.install_base))
        else:
            for sys_prefix in ["/usr/local", "/usr"]:
                if Path(sys_prefix).exists():
                    prefixes.append(Path(sys_prefix))
        
        for prefix in prefixes:
            desktop_file = prefix / "share" / "applications" / "draggg.desktop"
            
            if desktop_file.exists():
                try:
                    content = desktop_file.read_text()
                    # Ensure Icon=draggg
                    if "Icon=draggg" not in content:
                        content = re.sub(r'^Icon=.*$', 'Icon=draggg', content, flags=re.MULTILINE)
                        desktop_file.write_text(content)
                except Exception:
                    pass  # Silently continue
    
    def install_user_files(self):
        """Install desktop file and icons to user locations for --user installations."""
        import site
        import subprocess
        
        try:
            # Determine if user installation
            user_base = Path(site.getuserbase())
            if not user_base.exists():
                return  # Not a user installation or user_base not available
            
            # Check if this is actually a user installation
            # For user installs, install_base should be None or point to user location
            is_user_install = False
            if hasattr(self, 'install_base'):
                if self.install_base is None:
                    is_user_install = True
                else:
                    install_base_path = Path(self.install_base)
                    # Check if install_base is under user_base
                    try:
                        is_user_install = install_base_path.is_relative_to(user_base)
                    except AttributeError:
                        # Python < 3.9 compatibility
                        is_user_install = str(install_base_path).startswith(str(user_base))
            
            # Also check if --user flag was used
            if not is_user_install:
                # Check command line arguments
                if hasattr(self, 'user') and self.user:
                    is_user_install = True
            
            if not is_user_install:
                return  # System installation, skip user file installation
            
            # Install desktop file (always for user installs)
            desktop_source = Path(__file__).parent / "draggg.desktop"
            desktop_dest = user_base / "share" / "applications" / "draggg.desktop"
            if desktop_source.exists():
                desktop_dest.parent.mkdir(parents=True, exist_ok=True)
                # Read and ensure desktop file uses correct Exec and Icon
                desktop_content = desktop_source.read_text()
                # Ensure Exec=draggg-gui (entry point)
                if 'Exec=draggg-gui' not in desktop_content:
                    import re
                    desktop_content = re.sub(r'^Exec=.*$', 'Exec=draggg-gui', desktop_content, flags=re.MULTILINE)
                # Ensure Icon=draggg
                if 'Icon=draggg' not in desktop_content:
                    import re
                    desktop_content = re.sub(r'^Icon=.*$', 'Icon=draggg', desktop_content, flags=re.MULTILINE)
                desktop_dest.write_text(desktop_content)
                # Set executable permission
                desktop_dest.chmod(0o755)
            
            # Install icons
            icon_sizes = {
                '256x256': 'icon.png',
                '128x128': 'icon-128.png',
                '64x64': 'icon-64.png',
                '48x48': 'icon-48.png',
            }
            
            assets_dir = Path(__file__).parent / "assets"
            og_icon_dir = assets_dir / "og_icon"
            
            icons_installed = False
            for size, filename in icon_sizes.items():
                # Determine source path
                if filename == 'icon.png':
                    icon_source = og_icon_dir / filename
                elif filename == 'icon-128.png':
                    # icon-128.png is in assets/ directly
                    icon_source = assets_dir / filename
                else:
                    # icon-64.png and icon-48.png are in og_icon/
                    icon_source = og_icon_dir / filename
                
                # Fallback: try assets/ if og_icon/ doesn't have it
                if not icon_source.exists() and filename != 'icon-128.png':
                    icon_source = assets_dir / filename
                
                if icon_source.exists():
                    icon_dest = user_base / "share" / "icons" / "hicolor" / size / "apps" / "draggg.png"
                    icon_dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(icon_source, icon_dest)
                    icons_installed = True
            
            # Also create smaller sizes from 48x48 if available
            icon_48_source = og_icon_dir / "icon-48.png"
            if not icon_48_source.exists():
                icon_48_source = assets_dir / "icon-48.png"
            
            if icon_48_source.exists():
                smaller_sizes = ['32x32', '24x24', '22x22', '16x16']
                for size in smaller_sizes:
                    icon_dest = user_base / "share" / "icons" / "hicolor" / size / "apps" / "draggg.png"
                    icon_dest.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy(icon_48_source, icon_dest)
                        icons_installed = True
                    except Exception:
                        pass  # Optional sizes
            
            # Always update icon cache and desktop database if desktop entry or icons were installed
            if desktop_dest.exists() or icons_installed:
                self.update_desktop_integration(user_base)
        except Exception:
            # Don't fail installation if user file installation fails
            pass
    
    def update_desktop_integration(self, user_base: Path):
        """Update icon cache and desktop database after installing desktop entry and icons."""
        import subprocess
        
        try:
            # Update icon cache
            icon_cache_dir = user_base / "share" / "icons" / "hicolor"
            if icon_cache_dir.exists():
                subprocess.run(
                    ['gtk-update-icon-cache', '-f', '-t', str(icon_cache_dir)],
                    check=False,
                    capture_output=True,
                    timeout=10
                )
        except Exception:
            pass  # Non-critical
        
        try:
            # Update desktop database
            apps_dir = user_base / "share" / "applications"
            if apps_dir.exists():
                subprocess.run(
                    ['update-desktop-database', str(apps_dir)],
                    check=False,
                    capture_output=True,
                    timeout=10
                )
        except Exception:
            pass  # Non-critical


setup(
    name="draggg",
    version="1.0.17",
    description="macOS-style three-finger drag gestures for Linux trackpads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="draggg Contributors",
    url="https://github.com/j031nich0145/draggg",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    py_modules=["draggg_config", "draggg", "detect_hardware", "draggg_gui"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "draggg=draggg:main",
            "draggg-gui=draggg_gui:main",
            "wayland-to-x11=scripts.wayland_to_x11:main",
            "wayland-to-x11-tui=scripts.wayland_to_x11_tui:main",
            "draggg-setup=scripts.post_install_setup:main",
        ],
    },
    package_data={
        "": [
            "assets/*.png",
            "draggg.desktop",
            "draggg.service",
        ],
    },
    data_files=[
        ("share/applications", ["draggg.desktop"]),
        ("share/icons/hicolor/256x256/apps", ["assets/og_icon/icon.png"]),
        ("share/icons/hicolor/128x128/apps", ["assets/icon-128.png"]),
        ("share/icons/hicolor/64x64/apps", ["assets/og_icon/icon-64.png"]),
        ("share/icons/hicolor/48x48/apps", ["assets/og_icon/icon-48.png"]),
    ],
    keywords="touchpad gesture drag linux accessibility input",
    project_urls={
        "Bug Reports": "https://github.com/j031nich0145/draggg/issues",
        "Source": "https://github.com/j031nich0145/draggg",
        "Documentation": "https://github.com/j031nich0145/draggg#readme",
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)

