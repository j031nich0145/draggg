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
        except Exception as e:
            # Don't fail installation if post-install tasks fail
            pass  # Silent - don't print warnings during pip install
        
        # Launch background notification script (works in both interactive and non-interactive modes)
        try:
            # Find the installed script location
            import site
            user_base = Path(site.getuserbase())
            scripts_dir = user_base / "bin"
            
            # Try to launch post_install_notify.py from installed location
            notify_script = None
            
            # First try: installed scripts directory
            if scripts_dir.exists():
                # The script will be installed as a module, so we need to run it via Python
                try:
                    # Import and run in background
                    import subprocess
                    import os
                    
                    # Get Python executable
                    python_exe = sys.executable
                    
                    # Try to find the script in the installed package
                    try:
                        # Import the module to get its path
                        import scripts.post_install_notify
                        script_path = Path(scripts.post_install_notify.__file__)
                    except ImportError:
                        # Fallback: try relative to setup.py
                        script_path = Path(__file__).parent / "scripts" / "post_install_notify.py"
                    
                    if script_path.exists():
                        # Launch in background (detached process)
                        if os.name == 'nt':  # Windows
                            subprocess.Popen(
                                [python_exe, str(script_path)],
                                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                        else:  # Unix/Linux
                            subprocess.Popen(
                                [python_exe, str(script_path)],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                start_new_session=True
                            )
                except Exception:
                    # Silently fail - don't break pip install
                    pass
        except Exception:
            # Silently fail - don't break pip install
            pass
    
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


setup(
    name="draggg",
    version="1.0.5",
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
        ("share/icons/hicolor/256x256/apps", ["assets/icon.png"]),
        ("share/icons/hicolor/128x128/apps", ["assets/icon-128.png"]),
        ("share/icons/hicolor/64x64/apps", ["assets/icon-64.png"]),
        ("share/icons/hicolor/48x48/apps", ["assets/icon-48.png"]),
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

