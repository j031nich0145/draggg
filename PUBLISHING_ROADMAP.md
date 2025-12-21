# draggg Publishing Roadmap

This document outlines the step-by-step process for publishing draggg to various package repositories and distribution channels.

## Overview

This roadmap covers publishing to:
- **pip/PyPI** - Python Package Index (primary distribution)
- **snap/Snap Store** - Universal Linux packages
- **apt/Debian** - Debian/Ubuntu repositories
- **conda/conda-forge** - Anaconda/Miniconda distribution

## Prerequisites

### Accounts and Access

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Enable two-factor authentication (recommended)
   - Note: You'll need separate accounts for TestPyPI and PyPI

2. **Snapcraft Account**
   - Create account at https://snapcraft.io/
   - Verify email address
   - Complete profile information

3. **GitHub Releases**
   - Ensure repository is on GitHub
   - Set up GitHub Actions for automated releases (optional)

4. **GPG Key (for Debian packages)**
   - Generate GPG key: `gpg --gen-key`
   - Export public key for repository signing

### Tools Required

- `twine` - For uploading to PyPI
- `snapcraft` - For building snap packages
- `dpkg-buildpackage` - For building Debian packages
- `dput` or `reprepro` - For uploading to Debian repositories
- `conda-build` - For building conda packages

---

## 1. pip/PyPI Publishing

### Step 1: Prepare Package

1. **Update version in `setup.py`:**
   ```python
   version='1.0.0',  # Update version number
   ```

2. **Update version in all package files:**
   - `setup.py`
   - `snap/snapcraft.yaml`
   - `debian/changelog`
   - `conda/meta.yaml`
   - `README.md` (if version mentioned)

3. **Build package:**
   ```bash
   python3 setup.py sdist bdist_wheel
   ```

4. **Verify build:**
   ```bash
   ls -lh dist/
   # Should see: draggg-1.0.0.tar.gz and draggg-1.0.0-py3-none-any.whl
   ```

### Step 2: Test on TestPyPI

1. **Install twine:**
   ```bash
   pip install twine
   ```

2. **Upload to TestPyPI:**
   ```bash
   twine upload --repository testpypi dist/*
   # Enter TestPyPI credentials when prompted
   ```

3. **Test installation:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ draggg
   draggg --help
   draggg-gui
   ```

4. **Uninstall test version:**
   ```bash
   pip uninstall draggg
   ```

### Step 3: Publish to PyPI

1. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   # Enter PyPI credentials when prompted
   ```

2. **Verify publication:**
   - Visit https://pypi.org/project/draggg/
   - Check package page loads correctly
   - Verify download statistics appear

3. **Test installation:**
   ```bash
   pip install draggg
   draggg --help
   draggg-gui
   ```

### Step 4: Update Documentation

1. Update README.md with actual PyPI installation command
2. Update any version-specific documentation
3. Create GitHub release notes

### Checklist

- [ ] Version updated in all files
- [ ] Package builds successfully
- [ ] Tested on TestPyPI
- [ ] Published to PyPI
- [ ] Installation verified
- [ ] Documentation updated

---

## 2. snap/Snap Store Publishing

### Step 1: Prepare Snap Package

1. **Verify `snap/snapcraft.yaml`:**
   - Check name, version, summary, description
   - Verify apps section (draggg, draggg-gui, draggg-service)
   - Check plugs (hardware-observer, x11, desktop)
   - Verify Python plugin configuration

2. **Build snap locally:**
   ```bash
   snapcraft
   # This creates draggg_1.0.0_amd64.snap
   ```

3. **Test snap locally:**
   ```bash
   sudo snap install draggg_1.0.0_amd64.snap --dangerous
   snap run draggg --help
   snap run draggg-gui
   ```

4. **Test permissions:**
   ```bash
   snap connect draggg:hardware-observer
   snap connect draggg:x11
   ```

### Step 2: Register Snap Name

1. **Register name on Snap Store:**
   ```bash
   snapcraft login
   snapcraft register draggg
   ```

2. **Verify name registration:**
   - Visit https://snapcraft.io/draggg
   - Name should show as available or registered

### Step 3: Upload to Snap Store

1. **Upload for review:**
   ```bash
   snapcraft upload draggg_1.0.0_amd64.snap --release=stable
   ```

2. **Monitor review:**
   - Check email for review status
   - Address any review comments
   - May take 1-3 days for initial review

3. **Release to channels:**
   ```bash
   # After approval, release to stable
   snapcraft release draggg 1 stable
   
   # Or use web interface at https://snapcraft.io/draggg/releases
   ```

### Step 4: Update Documentation

1. Update README.md with snap installation instructions
2. Add snap store badge to README
3. Document permission setup requirements

### Checklist

- [ ] Snap builds successfully
- [ ] Tested locally with --dangerous
- [ ] Snap name registered
- [ ] Uploaded to Snap Store
- [ ] Review approved
- [ ] Released to stable channel
- [ ] Installation verified from store
- [ ] Documentation updated

---

## 3. apt/Debian Publishing

### Option A: Personal Package Archive (PPA)

#### Step 1: Set Up Launchpad Account

1. **Create Launchpad account:**
   - Sign up at https://launchpad.net/
   - Verify email address
   - Set up SSH keys for uploads

2. **Create PPA:**
   - Go to https://launchpad.net/+new-ppa
   - Name: `draggg` or `draggg/stable`
   - Description: "draggg three-finger drag gesture handler"

#### Step 2: Build and Upload

1. **Install build tools:**
   ```bash
   sudo apt install build-essential devscripts debhelper
   ```

2. **Build package:**
   ```bash
   cd draggg
   dpkg-buildpackage -S -us -uc  # Source package
   ```

3. **Upload to PPA:**
   ```bash
   dput ppa:yourusername/draggg ../draggg_1.0.0_source.changes
   ```

4. **Monitor build:**
   - Check https://launchpad.net/~yourusername/+archive/ubuntu/draggg
   - Wait for package to build (usually 30-60 minutes)

#### Step 3: Add PPA Instructions

Users can then install via:
```bash
sudo add-apt-repository ppa:yourusername/draggg
sudo apt update
sudo apt install draggg
```

### Option B: Debian Repository

#### Step 1: Set Up Repository Hosting

1. **Choose hosting:**
   - GitHub Releases (simple)
   - Dedicated repository server
   - Package hosting service

2. **Create repository structure:**
   ```
   repo/
   ├── dists/
   │   └── stable/
   │       ├── main/
   │       │   ├── binary-amd64/
   │       │   └── binary-arm64/
   │       └── Release
   └── pool/
       └── main/
           └── d/
               └── draggg/
   ```

#### Step 2: Build and Sign Packages

1. **Build binary package:**
   ```bash
   dpkg-buildpackage -b
   ```

2. **Sign package:**
   ```bash
   debsign -k YOUR_GPG_KEY_ID ../draggg_1.0.0_amd64.changes
   ```

3. **Create repository:**
   ```bash
   reprepro -b /path/to/repo includedeb stable ../draggg_1.0.0_amd64.deb
   ```

#### Step 3: Host Repository

1. **Upload repository files:**
   - Upload to web server
   - Ensure proper directory structure
   - Set correct permissions

2. **Create repository configuration:**
   - Generate Release file
   - Sign Release file with GPG
   - Serve over HTTPS

### Checklist

- [ ] Launchpad account created (PPA) or repository hosting set up
- [ ] Package builds successfully
- [ ] Packages uploaded
- [ ] Repository accessible
- [ ] Installation instructions documented
- [ ] GPG key distributed (for custom repos)

---

## 4. conda/conda-forge Publishing

### Step 1: Fork conda-forge Staged Recipes

1. **Fork repository:**
   - Go to https://github.com/conda-forge/staged-recipes
   - Fork the repository

2. **Create recipe branch:**
   ```bash
   git clone https://github.com/yourusername/staged-recipes.git
   cd staged-recipes
   git checkout -b draggg
   ```

### Step 2: Create Recipe

1. **Create recipe directory:**
   ```bash
   mkdir recipes/draggg
   ```

2. **Copy and customize `meta.yaml`:**
   - Use `conda/meta.yaml` as base
   - Ensure all dependencies listed
   - Set correct version and build number
   - Add test commands

3. **Create `build.sh` (if needed):**
   - Usually not needed for pure Python packages
   - May need for binary dependencies

### Step 3: Submit PR

1. **Commit and push:**
   ```bash
   git add recipes/draggg/
   git commit -m "Add draggg recipe"
   git push origin draggg
   ```

2. **Create pull request:**
   - Go to conda-forge/staged-recipes
   - Create PR from your branch
   - Fill out PR template completely

3. **Respond to review:**
   - Address any feedback
   - Update recipe as needed
   - Re-run CI tests

### Step 4: Maintain Feedstock

1. **After PR merged:**
   - A new feedstock repository will be created
   - `conda-forge/draggg-feedstock`
   - You'll be added as maintainer

2. **Update recipe:**
   - Fork feedstock repository
   - Update `meta.yaml` with new version
   - Submit PR to feedstock
   - CI will build and publish automatically

### Checklist

- [ ] Recipe created in staged-recipes
- [ ] PR submitted and reviewed
- [ ] Feedstock repository created
- [ ] Maintainer access granted
- [ ] Package available on conda-forge
- [ ] Installation tested: `conda install -c conda-forge draggg`

---

## Version Management

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Updating Versions

When releasing a new version, update in this order:

1. **Source files:**
   - `setup.py` - version field
   - `draggg/__init__.py` (if exists) - `__version__`

2. **Package files:**
   - `snap/snapcraft.yaml` - version field
   - `debian/changelog` - new entry with version
   - `conda/meta.yaml` - version and build number

3. **Documentation:**
   - `README.md` - version mentions
   - `CHANGELOG.md` - new version entry

4. **Git:**
   - Tag release: `git tag -a v1.0.0 -m "Release version 1.0.0"`
   - Push tag: `git push origin v1.0.0`

---

## Testing Before Publishing

### Pre-Publication Checklist

1. **Code Quality:**
   - [ ] All tests pass
   - [ ] No linter errors
   - [ ] Code reviewed

2. **Functionality:**
   - [ ] GUI works correctly
   - [ ] Service installs and runs
   - [ ] All features tested
   - [ ] No critical bugs

3. **Packaging:**
   - [ ] Package builds successfully
   - [ ] All files included (check MANIFEST.in)
   - [ ] Dependencies correct
   - [ ] Entry points work

4. **Documentation:**
   - [ ] README updated
   - [ ] Installation instructions clear
   - [ ] Troubleshooting section complete
   - [ ] Version numbers consistent

5. **Testing Installation:**
   - [ ] Fresh install test (clean environment)
   - [ ] Upgrade test (from previous version)
   - [ ] Uninstall test
   - [ ] All package formats tested

---

## Post-Publishing Tasks

### Immediate (Day 1)

1. **Verify Installations:**
   - Test installation from each published source
   - Verify all entry points work
   - Check desktop entries and icons appear

2. **Monitor Issues:**
   - Watch for user reports
   - Monitor download statistics
   - Check for build failures

3. **Update Documentation:**
   - Update README with actual installation commands
   - Add badges/links to package pages
   - Update changelog

### Short Term (Week 1)

1. **Marketing/Announcement:**
   - Announce on social media
   - Post on relevant forums/communities
   - Submit to software directories

2. **Collect Feedback:**
   - Monitor GitHub issues
   - Respond to user questions
   - Address any critical bugs

3. **Update Metadata:**
   - Update package descriptions if needed
   - Add screenshots/videos
   - Improve documentation based on feedback

### Ongoing Maintenance

1. **Regular Updates:**
   - Bug fixes → Patch version bump
   - New features → Minor version bump
   - Breaking changes → Major version bump

2. **Monitor Repositories:**
   - Check for dependency updates
   - Security advisories
   - Deprecation warnings

3. **Maintain Packages:**
   - Keep all package formats up to date
   - Respond to package manager reviews
   - Maintain conda-forge feedstock

---

## Quick Reference Checklist

### pip/PyPI
- [ ] Update version in setup.py
- [ ] Build: `python3 setup.py sdist bdist_wheel`
- [ ] Test on TestPyPI
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify at https://pypi.org/project/draggg/

### snap/Snap Store
- [ ] Update version in snapcraft.yaml
- [ ] Build: `snapcraft`
- [ ] Test locally: `sudo snap install *.snap --dangerous`
- [ ] Register name: `snapcraft register draggg`
- [ ] Upload: `snapcraft upload *.snap --release=stable`
- [ ] Verify at https://snapcraft.io/draggg

### apt/Debian
- [ ] Update version in debian/changelog
- [ ] Build: `dpkg-buildpackage -b`
- [ ] Sign package (if needed)
- [ ] Upload to PPA or repository
- [ ] Verify installation

### conda/conda-forge
- [ ] Update recipe in staged-recipes or feedstock
- [ ] Submit PR
- [ ] Address review feedback
- [ ] Verify at https://anaconda.org/conda-forge/draggg

---

## Troubleshooting

### Common Issues

**Package build fails:**
- Check all dependencies are listed
- Verify file paths in MANIFEST.in or package configs
- Check for syntax errors in config files

**Upload fails:**
- Verify credentials are correct
- Check package name availability
- Ensure version number is unique

**Installation issues:**
- Test in clean environment
- Check dependency resolution
- Verify entry points are correct

**Review rejected:**
- Address all review comments
- Update package metadata
- Fix any security/quality issues

---

## Resources

- **PyPI Documentation:** https://packaging.python.org/
- **Snap Store Guide:** https://snapcraft.io/docs
- **Debian Packaging:** https://www.debian.org/doc/manuals/packaging-tutorial/
- **conda-forge Guide:** https://conda-forge.org/docs/

---

*Last Updated: 2025-12-20*
*Version: 1.0*

