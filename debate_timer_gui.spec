# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

tcl_base = 'C:\\Users\\manman\\AppData\\Local\\Programs\\Python\\Python313\\tcl'
tkinter_dll_path = 'C:\\Users\\manman\\AppData\\Local\\Programs\\Python\\Python313\\DLLs'

a = Analysis(
    ['debate_timer_gui.py'],
    pathex=['D:\\学习资料2\\umc'],
    binaries=[
        (tkinter_dll_path + '\\_tkinter.pyd', '.'),
        (tkinter_dll_path + '\\tcl86t.dll', '.'),
        (tkinter_dll_path + '\\tk86t.dll', '.'),
    ],
    datas=[
        (tcl_base + '\\tcl8.6', '_tcl_data'),
        (tcl_base + '\\tk8.6', '_tk_data'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk', 
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        '_tkinter',
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
    [],
    exclude_binaries=True,
    name='辩论计时器GUI',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='辩论计时器GUI',
)
