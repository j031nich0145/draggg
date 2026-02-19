# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for draggg (Windows)

block_cipher = None

a = Analysis(
    ['draggg.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('draggg.desktop', '.'),
        ('config.py', '.'),
        ('detect_hardware.py', '.'),
    ],
    hiddenimports=[
        'config',
        'detect_hardware',
        'gui',
        'gui.setup_wizard',
        'gui.settings_panel',
        'gui.utils',
        'gui.widgets',
        'scripts',
        'scripts.post_install_setup',
        'scripts.wayland_to_x11',
        'scripts.wayland_to_x11_tui',
        'scripts.desktop_notify',
        'scripts.post_install_notify',
        'evdev',
        'uinput',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='draggg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon-128.png',
)
