#!/usr/bin/env python3
"""
Setup script for draggg - Three-Finger Drag for Linux
"""

from setuptools import setup, find_packages
from pathlib import Path

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

setup(
    name="draggg",
    version="1.0.0",
    description="macOS-style three-finger drag gestures for Linux trackpads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="draggg Contributors",
    url="https://github.com/yourusername/draggg",
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
    py_modules=["config", "draggg", "detect_hardware"],
    entry_points={
        "console_scripts": [
            "draggg=draggg:main",
            "draggg-gui=draggg_gui:main",
        ],
    },
    include_package_data=True,
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
        "Bug Reports": "https://github.com/yourusername/draggg/issues",
        "Source": "https://github.com/yourusername/draggg",
        "Documentation": "https://github.com/yourusername/draggg#readme",
    },
)

