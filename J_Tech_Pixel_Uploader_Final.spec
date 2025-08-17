# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all required data files
datas = [
    ('config.py', '.'),
    ('utils.py', '.'),
    ('SampleFirmware', 'SampleFirmware'),
    ('README.md', '.'),
    ('DEPENDENCY_INSTALLER_README.md', '.'),
    ('requirements.txt', '.')
]

# Collect hidden imports
hiddenimports = [
    'serial',
    'serial.tools.list_ports',
    'esptool',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'threading',
    'subprocess',
    'datetime',
    'importlib.util',
    'os',
    'sys',
    'time'
]

# Exclude unnecessary modules to reduce size
excludes = [
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'cv2',
    'tensorflow',
    'torch',
    'jupyter',
    'notebook',
    'IPython',
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'profile',
    'cProfile',
    'pstats',
    'trace',
    'distutils',
    'setuptools',
    'pip',
    'wheel',
    'pkg_resources'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='J_Tech_Pixel_Uploader_v2.0_Final',
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
    uac_admin=False,
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='J_Tech_Pixel_Uploader_v2.0_Final'
)
