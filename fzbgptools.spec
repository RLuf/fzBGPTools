# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for fzBGPTools — relative paths, cross-platform.
# Build:  pyinstaller --noconfirm fzbgptools.spec
import sys
from pathlib import Path

ROOT = Path(SPECPATH)

is_windows = sys.platform.startswith("win")
is_mac     = sys.platform == "darwin"

icon_png = str(ROOT / "src" / "resources" / "icon.png")
icon_ico = str(ROOT / "src" / "resources" / "icon.ico") if (ROOT / "src" / "resources" / "icon.ico").exists() else None
icon_icns= str(ROOT / "src" / "resources" / "icon.icns") if (ROOT / "src" / "resources" / "icon.icns").exists() else None

datas = [
    (str(ROOT / "src" / "resources"), "src/resources"),
]

block_cipher = None

a = Analysis(
    [str(ROOT / "src" / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "paramiko", "cryptography",
        "PyQt5.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "scipy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Pick icon by platform
exe_icon = None
if is_windows and icon_ico:
    exe_icon = icon_ico
elif is_mac and icon_icns:
    exe_icon = icon_icns

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='fzbgptools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
)

if is_mac:
    app = BUNDLE(
        exe,
        name='fzBGPTools.app',
        icon=icon_icns,
        bundle_identifier='com.fzbgptools.app',
        info_plist={
            'CFBundleShortVersionString': '0.2.0',
            'NSHighResolutionCapable': 'True',
        },
    )
