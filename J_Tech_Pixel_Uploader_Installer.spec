# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all necessary data files
datas = [
    ('config.py', '.'),
    ('utils.py', '.'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('SampleFirmware', 'SampleFirmware'),
]

# Collect hidden imports
hiddenimports = [
    'serial',
    'serial.tools.list_ports',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'threading',
    'subprocess',
    'datetime',
    'os',
    'time',
    'json',
    'config',
    'utils'
]

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='J_Tech_Pixel_Uploader_v2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version_file=None,
)

# Create collection
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='J_Tech_Pixel_Uploader_v2.0'
)

# Create installer
installer = EXE(
    coll,
    [],
    name='J_Tech_Pixel_Uploader_Setup_v2.0.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)
