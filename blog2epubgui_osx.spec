# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [
        'blog2epubkivy.py'
    ],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(
    a.pure, a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='blog2epub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='blog2epub.icns'
)
info_plist = {
    "NSHighResolutionCapable": True,
}
app = BUNDLE(
    exe,
    name='blog2epub.app',
    icon='images/blog2epub.icns',
    bundle_identifier=None,
    info_plist=info_plist
)
