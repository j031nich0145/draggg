# Version Management and PyPI Publishing Guide

This guide explains how to manage versions and publish `draggg` to PyPI.

## Version Number Format

Versions follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.0.12 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 1.0.12 → 1.1.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 1.0.12 → 1.0.13)

## Version Storage

Version numbers are stored in **4 files**:

1. `setup.py` (line 354): `version="1.0.12"`
2. `pyproject.toml` (line 7): `version = "1.0.12"`
3. `conda/meta.yaml` (line 2): `{% set version = "1.0.12" %}`
4. `gui/__init__.py` (line 5): `__version__ = "1.0.12"`

## Publishing Methods

### Method 1: Automatic Publishing (Recommended)

**How it works:**
- Push commits to `main` branch
- GitHub Actions automatically increments the **patch version** (e.g., 1.0.12 → 1.0.13)
- Builds and publishes to PyPI if version doesn't exist
- Creates a git tag automatically

**Steps:**
1. Make your changes
2. Commit and push to `main`:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```
3. GitHub Actions will:
   - Auto-increment patch version
   - Update all 4 version files
   - Build package
   - Check if version exists on PyPI
   - Publish if new version
   - Create git tag (e.g., `v1.0.13`)

**Note:** This method only increments the **patch** version. For major/minor updates, use Method 2 or 3.

### Method 2: Manual Version Update with Script

Use the provided script to update all version files at once:

**Steps:**
1. Update version using the script:
   ```bash
   python scripts/update_version.py 1.0.13
   # Or for minor version:
   python scripts/update_version.py 1.1.0
   # Or for major version:
   python scripts/update_version.py 2.0.0
   ```

2. Review changes:
   ```bash
   git diff
   ```

3. Commit and push:
   ```bash
   git add setup.py pyproject.toml conda/meta.yaml gui/__init__.py
   git commit -m "Bump version to 1.0.13"
   git push origin main
   ```

4. GitHub Actions will:
   - Detect the version change
   - Build and publish to PyPI
   - Create git tag automatically

### Method 3: Tag-Based Publishing

Create a version tag manually:

**Steps:**
1. Update version manually in all 4 files OR use the script:
   ```bash
   python scripts/update_version.py 1.0.13
   ```

2. Commit the version changes:
   ```bash
   git add setup.py pyproject.toml conda/meta.yaml gui/__init__.py
   git commit -m "Bump version to 1.0.13"
   ```

3. Create and push the tag:
   ```bash
   git tag v1.0.13
   git push origin v1.0.13
   ```

4. GitHub Actions will:
   - Detect the tag
   - Build and publish to PyPI
   - Use the version from the tag

### Method 4: Manual Workflow Trigger

Trigger the workflow manually without pushing:

**Steps:**
1. Go to GitHub Actions tab
2. Select "Publish to PyPI" workflow
3. Click "Run workflow" → "Run workflow"
4. The workflow will use the current version in `setup.py`

**Note:** This method does NOT auto-increment the version. Make sure you've updated the version files first.

## Version Update Script

The `scripts/update_version.py` script automates version updates:

**Usage:**
```bash
python scripts/update_version.py VERSION
```

**Examples:**
```bash
# Patch version update
python scripts/update_version.py 1.0.13

# Minor version update
python scripts/update_version.py 1.1.0

# Major version update
python scripts/update_version.py 2.0.0
```

**What it does:**
- Validates version format (must be `MAJOR.MINOR.PATCH`)
- Updates all 4 version files automatically
- Shows success/error messages
- Provides next steps

**Error handling:**
- Invalid version format → Shows error and exits
- File not found → Shows error for that file
- Update failure → Shows which files failed

## Version Badge

The PyPI version badge in `README.md` uses shields.io and **automatically updates** when a new version is published to PyPI:

```markdown
[![PyPI version](https://img.shields.io/pypi/v/draggg.svg?label=PyPI)](https://pypi.org/project/draggg/)
```

The badge:
- Fetches the latest version from PyPI automatically
- Updates within minutes of publishing
- Links to the PyPI project page

## Workflow Behavior

### On Push to `main`:
- ✅ Auto-increments patch version (1.0.12 → 1.0.13)
- ✅ Updates all 4 version files
- ✅ Builds package
- ✅ Checks if version exists on PyPI
- ✅ Publishes if new version
- ✅ Creates git tag automatically

### On Tag Push (`v*`):
- ✅ Uses version from tag
- ✅ Builds package
- ✅ Checks if version exists on PyPI
- ✅ Publishes if new version
- ❌ Does NOT auto-increment (uses tag version)

### On Manual Trigger:
- ✅ Uses current version in `setup.py`
- ✅ Builds package
- ✅ Checks if version exists on PyPI
- ✅ Publishes if new version
- ❌ Does NOT auto-increment

## Troubleshooting

### Version Already Exists on PyPI

**Error:** `File already exists ('draggg-1.0.12-py3-none-any.whl')`

**Solution:**
- The workflow checks PyPI before publishing
- If version exists, it skips upload
- Increment to a new version:
  ```bash
  python scripts/update_version.py 1.0.13
  ```

### Version Not Updating

**Check:**
1. All 4 files have the same version:
   ```bash
   grep -r "version\|__version__" setup.py pyproject.toml conda/meta.yaml gui/__init__.py
   ```

2. Version format is correct (MAJOR.MINOR.PATCH)

3. Files are committed and pushed

### Workflow Not Triggering

**Check:**
1. Push is to `main` branch (not a feature branch)
2. Tag format is `v*` (e.g., `v1.0.13`, not `1.0.13`)
3. GitHub Actions is enabled for the repository
4. `PYPI_API_TOKEN` secret is set in repository settings

## Best Practices

1. **Use semantic versioning**: Follow MAJOR.MINOR.PATCH format
2. **Update all files**: Always update all 4 version files together
3. **Use the script**: Use `scripts/update_version.py` to avoid mistakes
4. **Test before publishing**: Test locally before pushing
5. **Check PyPI**: Verify the published version on https://pypi.org/project/draggg/

## Quick Reference

**Update version:**
```bash
python scripts/update_version.py 1.0.13
git add setup.py pyproject.toml conda/meta.yaml gui/__init__.py
git commit -m "Bump version to 1.0.13"
git push origin main
```

**Check current version:**
```bash
grep version setup.py pyproject.toml conda/meta.yaml gui/__init__.py
```

**View published versions:**
- PyPI: https://pypi.org/project/draggg/#history
- GitHub Releases: https://github.com/j031nich0145/draggg/releases
