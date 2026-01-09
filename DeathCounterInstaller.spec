# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['installer.py'],
    pathex=[],
    binaries=[],
    datas=[('multi_game_death_counter.py', '.'), ('death_counter_gui.py', '.'), ('death_counter_settings.py', '.'), ('log_monitor.py', '.'), ('memory_scanner.py', '.'), ('games_config.json', '.'), ('reset_death_counter.py', '.'), ('switch_game_manual.py', '.'), ('capture_debug_once.py', '.'), ('change_monitor_id.py', '.'), ('requirements.txt', '.'), ('README.md', '.'), ('FUZZY_MATCHING_GUIDE.md', '.')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='DeathCounterInstaller',
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
