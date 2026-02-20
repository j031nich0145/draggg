#!/usr/bin/env python3
"""
Update version number across all package files.

Usage:
    python scripts/update_version.py 1.0.13
    python scripts/update_version.py 1.1.0
"""

import re
import sys
from pathlib import Path


def validate_version(version: str) -> bool:
    """Validate version format (semantic versioning: MAJOR.MINOR.PATCH)."""
    return bool(re.match(r'^\d+\.\d+\.\d+$', version))


def update_setup_py(version: str, repo_root: Path) -> bool:
    """Update version in setup.py."""
    setup_py = repo_root / "setup.py"
    if not setup_py.exists():
        print(f"ERROR: {setup_py} not found")
        return False
    
    try:
        content = setup_py.read_text()
        # Match version="X.Y.Z"
        pattern = r'version="([^"]+)"'
        match = re.search(pattern, content)
        if not match:
            print(f"ERROR: Could not find version in {setup_py}")
            return False
        
        old_version = match.group(1)
        new_content = re.sub(pattern, f'version="{version}"', content)
        setup_py.write_text(new_content)
        print(f"✓ Updated {setup_py}: {old_version} → {version}")
        return True
    except Exception as e:
        print(f"ERROR updating {setup_py}: {e}")
        return False


def update_pyproject_toml(version: str, repo_root: Path) -> bool:
    """Update version in pyproject.toml."""
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        print(f"ERROR: {pyproject} not found")
        return False
    
    try:
        content = pyproject.read_text()
        # Match version = "X.Y.Z"
        pattern = r'version = "([^"]+)"'
        match = re.search(pattern, content)
        if not match:
            print(f"ERROR: Could not find version in {pyproject}")
            return False
        
        old_version = match.group(1)
        new_content = re.sub(pattern, f'version = "{version}"', content)
        pyproject.write_text(new_content)
        print(f"✓ Updated {pyproject}: {old_version} → {version}")
        return True
    except Exception as e:
        print(f"ERROR updating {pyproject}: {e}")
        return False


def update_conda_meta_yaml(version: str, repo_root: Path) -> bool:
    """Update version in conda/meta.yaml."""
    meta_yaml = repo_root / "conda" / "meta.yaml"
    if not meta_yaml.exists():
        print(f"WARNING: {meta_yaml} not found (skipping)")
        return True  # Not critical if conda recipe doesn't exist
    
    try:
        content = meta_yaml.read_text()
        # Match {% set version = "X.Y.Z" %}
        pattern = r'\{% set version = "([^"]+)" %\}'
        match = re.search(pattern, content)
        if not match:
            print(f"ERROR: Could not find version in {meta_yaml}")
            return False
        
        old_version = match.group(1)
        new_content = re.sub(pattern, f'{{% set version = "{version}" %}}', content)
        meta_yaml.write_text(new_content)
        print(f"✓ Updated {meta_yaml}: {old_version} → {version}")
        return True
    except Exception as e:
        print(f"ERROR updating {meta_yaml}: {e}")
        return False


def update_gui_init(version: str, repo_root: Path) -> bool:
    """Update version in gui/__init__.py."""
    gui_init = repo_root / "gui" / "__init__.py"
    if not gui_init.exists():
        print(f"ERROR: {gui_init} not found")
        return False
    
    try:
        content = gui_init.read_text()
        # Match __version__ = "X.Y.Z"
        pattern = r'__version__ = "([^"]+)"'
        match = re.search(pattern, content)
        if not match:
            print(f"ERROR: Could not find version in {gui_init}")
            return False
        
        old_version = match.group(1)
        new_content = re.sub(pattern, f'__version__ = "{version}"', content)
        gui_init.write_text(new_content)
        print(f"✓ Updated {gui_init}: {old_version} → {version}")
        return True
    except Exception as e:
        print(f"ERROR updating {gui_init}: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_version.py VERSION")
        print("Example: python scripts/update_version.py 1.0.13")
        sys.exit(1)
    
    new_version = sys.argv[1].strip()
    
    # Validate version format
    if not validate_version(new_version):
        print(f"ERROR: Invalid version format: {new_version}")
        print("Expected format: MAJOR.MINOR.PATCH (e.g., 1.0.13)")
        sys.exit(1)
    
    # Get repository root (parent of scripts directory)
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    
    print(f"Updating version to {new_version}...")
    print()
    
    # Update all files
    results = [
        update_setup_py(new_version, repo_root),
        update_pyproject_toml(new_version, repo_root),
        update_conda_meta_yaml(new_version, repo_root),
        update_gui_init(new_version, repo_root),
    ]
    
    print()
    if all(results):
        print(f"✓ Successfully updated version to {new_version} in all files!")
        print()
        print("Next steps:")
        print("  1. Review the changes: git diff")
        print("  2. Commit: git add -u && git commit -m 'Bump version to {new_version}'")
        print("  3. Push to main (auto-publishes) or create tag: git tag v{new_version}")
        sys.exit(0)
    else:
        print("ERROR: Some files could not be updated. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
