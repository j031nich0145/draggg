# Building draggg Snap Package

## Option 1: Destructive Mode (No LXD Required) - Recommended

Build the snap directly on your system without containers:

```bash
cd /home/ubu/Documents/BUILD/draggg
snapcraft pack --destructive-mode
```

This builds directly on your host system. Note: This may install packages on your system temporarily.

## Option 2: Set Up LXD (For Container-Based Builds)

If you prefer container-based builds (more isolated):

### Step 1: Add yourself to lxd group
```bash
sudo usermod -aG lxd $USER
```

### Step 2: Log out and log back in
Or run:
```bash
newgrp lxd
```

### Step 3: Initialize LXD
```bash
sudo lxd init --auto
```

### Step 4: Build snap
```bash
cd /home/ubu/Documents/BUILD/draggg
snapcraft pack
```

## Building for Specific Architecture

```bash
# Build for amd64 (default)
snapcraft pack --destructive-mode --build-for=amd64

# Build for arm64 (cross-compilation)
snapcraft pack --destructive-mode --build-for=arm64
```

## Testing the Snap Locally

After building, test locally:

```bash
# Install locally (bypasses store)
sudo snap install draggg_1.0.5_amd64.snap --dangerous

# Test commands
snap run draggg --help
snap run draggg-gui

# Connect required interfaces
sudo snap connect draggg:hardware-observer
sudo snap connect draggg:x11
```

## Publishing to Snap Store

Once the snap builds successfully:

1. **Login to Snap Store:**
   ```bash
   snapcraft login
   ```

2. **Register the name (first time only):**
   ```bash
   snapcraft register draggg
   ```

3. **Upload to store:**
   ```bash
   snapcraft upload draggg_1.0.5_amd64.snap --release=stable
   ```

4. **Check status:**
   ```bash
   snapcraft status draggg
   ```

## Troubleshooting

**If destructive mode fails:**
- Make sure you have all build dependencies installed
- Check that Python 3.8+ is available
- Verify all system packages are installed

**If LXD setup fails:**
- Ensure you're in the lxd group: `groups | grep lxd`
- Try logging out and back in
- Initialize LXD: `sudo lxd init --auto`
