# Publishing draggg to Snap Store

Complete guide for publishing draggg to the Snap Store.

## Prerequisites

1. **Snapcraft Account**: Create account at https://snapcraft.io/
2. **Snapcraft CLI**: Install `snapcraft` (usually via `snap install snapcraft --classic`)
3. **LXD** (Optional): Required for container-based builds (user must be in `lxd` group)
   - For local builds without containers, use `--destructive-mode` flag
4. **Snap Store Login**: Run `snapcraft login` to authenticate

## Step-by-Step Publishing Process

### Step 1: Review snapcraft.yaml

Verify the configuration file is correct:

```bash
cd snap
cat snapcraft.yaml
```

**Key things to check:**
- Version matches current release (should match PyPI version)
- All plugs, apps, and parts are correct
- Build dependencies are listed
- Stage packages include all runtime dependencies

### Step 2: Build the Snap

**Option A: Destructive Mode (Recommended for local builds)**
```bash
cd snap
snapcraft pack --destructive-mode
```

This builds directly on your host system without containers. Note: This may install packages temporarily on your system.

**Option B: Container-Based Build (Requires LXD)**
```bash
# Ensure you're in lxd group
sudo usermod -aG lxd $USER
# Log out and back in, or run:
newgrp lxd

# Initialize LXD (first time only)
sudo lxd init --auto

# Build snap
cd snap
snapcraft pack
```

**Building for Specific Architectures:**
```bash
# Build for amd64 (default)
snapcraft pack --destructive-mode --build-for=amd64

# Build for arm64 (cross-compilation)
snapcraft pack --destructive-mode --build-for=arm64
```

This creates `draggg_<version>_<arch>.snap` in the snap directory.

### Step 3: Test the Snap Locally (Optional but Recommended)

Before publishing, test the snap locally:

```bash
# Install locally (bypasses store)
sudo snap install draggg_<version>_amd64.snap --dangerous

# Test all apps
snap run draggg --help
snap run draggg-gui
snap run draggg-service

# Connect required interfaces
sudo snap connect draggg:hardware-observer
sudo snap connect draggg:x11
sudo snap connect draggg:input-devices
```

**Uninstall test snap:**
```bash
sudo snap remove draggg
```

### Step 4: Register Snap Name (First Time Only)

If this is your first time publishing, register the snap name:

```bash
snapcraft register draggg
```

This reserves the name `draggg` in the Snap Store. You only need to do this once.

### Step 5: Login to Snap Store

Authenticate with your Snap Store account:

```bash
snapcraft login
```

Follow the prompts to authenticate via web browser.

### Step 6: Upload to Snap Store

Upload your snap to the store. Start with the `edge` channel for testing:

```bash
snapcraft upload draggg_<version>_amd64.snap --release=edge
```

**Channel Options:**
- `edge`: Development/testing releases (use this first)
- `beta`: Pre-release testing
- `candidate`: Release candidates
- `stable`: Production releases

**Upload to Multiple Channels:**
```bash
snapcraft upload draggg_<version>_amd64.snap --release=edge,beta
```

### Step 7: Check Upload Status

Verify your upload was successful:

```bash
snapcraft status draggg
```

This shows the current status of your snap in each channel.

### Step 8: Promote to Stable (After Testing)

Once you've tested the snap in edge/beta channels and confirmed it works correctly:

```bash
snapcraft promote draggg <version> stable
```

Replace `<version>` with the actual version number (e.g., `1.0.9`).

**Example:**
```bash
snapcraft promote draggg 1.0.9 stable
```

## Snap Store Channels Explained

- **edge**: Development/testing releases - Use for initial uploads and testing
- **beta**: Pre-release testing - Use after edge testing is complete
- **candidate**: Release candidates - Use for final testing before stable
- **stable**: Production releases - Use only after thorough testing

**Best Practice:** Always test in `edge` first, then promote through channels as you gain confidence.

## Version Management

- Update `version` in `snap/snapcraft.yaml` to match PyPI version
- Consider automating version sync in CI/CD
- Use semantic versioning (e.g., `1.0.9`)

## Updating an Existing Snap

When publishing a new version:

1. Update version in `snap/snapcraft.yaml`
2. Build the new snap: `snapcraft pack --destructive-mode`
3. Upload: `snapcraft upload draggg_<new_version>_amd64.snap --release=edge`
4. Test in edge channel
5. Promote: `snapcraft promote draggg <new_version> stable`

## Troubleshooting

### LXD Errors

**Problem:** "LXD is required but not installed" or permission errors

**Solution:**
```bash
# Add user to lxd group
sudo usermod -aG lxd $USER

# Log out and back in, or run:
newgrp lxd

# Initialize LXD
sudo lxd init --auto
```

**Alternative:** Use `--destructive-mode` to skip LXD requirement.

### Build Failures

**Problem:** Build fails with dependency errors

**Solution:**
- Check `snapcraft.yaml` syntax
- Verify all build dependencies are listed in `build-packages`
- Ensure all runtime dependencies are in `stage-packages`
- Check Python requirements in `python-requirements`

### Upload Errors

**Problem:** "Snap name not registered" or authentication errors

**Solution:**
- Register the snap name: `snapcraft register draggg`
- Re-authenticate: `snapcraft login`
- Verify credentials are valid

### Version Already Exists

**Problem:** "Version already exists in channel"

**Solution:**
- Update version in `snapcraft.yaml`
- Rebuild the snap
- Upload new version

## Verifying Your Published Snap

After publishing, users can install your snap:

```bash
# Install from Snap Store
sudo snap install draggg

# Install specific channel
sudo snap install draggg --channel=edge

# Check installed version
snap list draggg
```

## Additional Resources

- Snap Store Dashboard: https://snapcraft.io/dashboard
- Snapcraft Documentation: https://snapcraft.io/docs
- Snap Store Listing: https://snapcraft.io/draggg (after first publish)

## CI/CD Integration (Future)

Consider automating snap builds and publishing:
- Build snap on version tags
- Automatically upload to edge channel
- Manual promotion to stable after testing
