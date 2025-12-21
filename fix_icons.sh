#!/bin/bash
# Quick script to fix/install all draggg icons manually
# Use this if icons didn't install correctly through the GUI or setup script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "Installing all draggg icon sizes..."
echo "========================================="
echo ""

# Create all icon directories
for size in 256x256 128x128 64x64 48x48 32x32 24x24 22x22 16x16; do
    mkdir -p "$HOME/.local/share/icons/hicolor/$size/apps"
done

# Copy icons
echo "Copying icons..."
if [ -f "assets/icon.png" ]; then
    cp "assets/icon.png" "$HOME/.local/share/icons/hicolor/256x256/apps/draggg.png"
    echo "  ✓ Installed 256x256"
fi

if [ -f "assets/icon-128.png" ]; then
    cp "assets/icon-128.png" "$HOME/.local/share/icons/hicolor/128x128/apps/draggg.png"
    echo "  ✓ Installed 128x128"
fi

if [ -f "assets/icon-64.png" ]; then
    cp "assets/icon-64.png" "$HOME/.local/share/icons/hicolor/64x64/apps/draggg.png"
    echo "  ✓ Installed 64x64"
fi

if [ -f "assets/icon-48.png" ]; then
    cp "assets/icon-48.png" "$HOME/.local/share/icons/hicolor/48x48/apps/draggg.png"
    echo "  ✓ Installed 48x48"
    
    # Use 48x48 for smaller sizes
    cp "assets/icon-48.png" "$HOME/.local/share/icons/hicolor/32x32/apps/draggg.png"
    cp "assets/icon-48.png" "$HOME/.local/share/icons/hicolor/24x24/apps/draggg.png"
    cp "assets/icon-48.png" "$HOME/.local/share/icons/hicolor/22x22/apps/draggg.png"
    cp "assets/icon-48.png" "$HOME/.local/share/icons/hicolor/16x16/apps/draggg.png"
    echo "  ✓ Installed smaller sizes (32x32, 24x24, 22x22, 16x16)"
fi

echo ""
echo "Updating icon cache..."
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>&1
    echo "  ✓ Icon cache updated"
else
    echo "  ⚠ gtk-update-icon-cache not found (icons may not appear until logout/login)"
fi

echo ""
echo "Updating desktop database..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" 2>&1
    echo "  ✓ Desktop database updated"
else
    echo "  ⚠ update-desktop-database not found"
fi

echo ""
echo "========================================="
echo "Icon installation complete!"
echo "========================================="
echo ""
echo "Verification:"
echo "  Installed icon sizes:"
ls -1 "$HOME/.local/share/icons/hicolor"/*/apps/draggg.png 2>/dev/null | sed 's|.*/hicolor/||;s|/apps.*||' | while read size; do
    echo "    ✓ $size"
done
echo ""
echo "Note: You may need to log out/in or restart your desktop environment"
echo "      for icons to appear in application menus and toolbars."

