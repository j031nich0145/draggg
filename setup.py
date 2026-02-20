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
        
        # Launch background notification script (works in both interactive and non-interactive modes)
        self._launch_notification_script()
    
    def _launch_notification_script(self):
        """Launch post-install notification script with improved error handling."""
        import site
        import subprocess
        
        log_dir = Path.home() / ".config" / "draggg"
        log_file = log_dir / "post_install_error.log"
        
        try:
            # Ensure log directory exists
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Get Python executable
            python_exe = sys.executable
            
            # Try to find the script in the installed package
            script_path = None
            
            # First try: import the module to get its path
            try:
                import scripts.post_install_notify
                script_path = Path(scripts.post_install_notify.__file__)
            except ImportError:
                # Fallback: search in sys.path for installed package
                for path in sys.path:
                    candidate = Path(path) / "scripts" / "post_install_notify.py"
                    if candidate.exists():
                        script_path = candidate
                        break
                
                # Last resort: try relative to setup.py (for development installs)
                if not script_path:
                    dev_path = Path(__file__).parent / "scripts" / "post_install_notify.py"
                    if dev_path.exists():
                        script_path = dev_path
            
            if not script_path or not script_path.exists():
                with open(log_file, 'a') as f:
                    f.write(f"ERROR: Could not find post_install_notify.py\n")
                    f.write(f"Searched paths: {sys.path}\n")
                return
            
            # Verify required modules can be imported
            try:
                import scripts.desktop_notify
                import scripts.post_install_setup
            except ImportError as e:
                with open(log_file, 'a') as f:
                    f.write(f"ERROR: Required modules not importable: {e}\n")
                return
            
            # Launch script with error logging
            if os.name == 'nt':  # Windows
                subprocess.Popen(
                    [python_exe, str(script_path)],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdout=open(log_file, 'a'),
                    stderr=open(log_file, 'a')
                )
            else:  # Unix/Linux
                subprocess.Popen(
                    [python_exe, str(script_path)],
                    stdout=open(log_file, 'a'),
                    stderr=open(log_file, 'a'),
                    start_new_session=True
                )
        except Exception as e:
            # Log error instead of silently failing
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                with open(log_file, 'a') as f:
                    f.write(f"ERROR launching post-install script: {e}\n")
                    import traceback
                    f.write(traceback.format_exc())
            except Exception:
                pass  # If logging fails, silently continue
    
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
            
            # Install desktop file
            desktop_source = Path(__file__).parent / "draggg.desktop"
            desktop_dest = user_base / "share" / "applications" / "draggg.desktop"
            if desktop_source.exists():
                desktop_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(desktop_source, desktop_dest)
            
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
            
            # Update icon cache and desktop database
            if icons_installed or desktop_dest.exists():
                try:
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
        except Exception:
            # Don't fail installation if user file installation fails
            pass


setup(
    name="draggg",
    version="1.0.11",
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    py_modules=["config", "draggg", "detect_hardware", "draggg_gui"],
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

