# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config.py', '.'), ('utils.py', '.'), ('SampleFirmware', 'SampleFirmware'), ('README.md', '.'), ('DEPENDENCY_INSTALLER_README.md', '.'), ('requirements.txt', '.')],
    hiddenimports=['serial', 'serial.tools.list_ports', 'esptool', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'threading', 'subprocess', 'datetime', 'importlib.util'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2', 'tensorflow', 'torch', 'jupyter', 'notebook', 'IPython', 'pytest', 'unittest', 'doctest', 'pdb', 'profile', 'cProfile', 'pstats', 'trace', 'distutils', 'setuptools', 'pip', 'wheel', 'pkg_resources'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='J_Tech_Pixel_Uploader_v2.0_Final',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
