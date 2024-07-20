# -*- mode: python ; coding: utf-8 -*-
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal

block_cipher = None
a = Analysis(
    ['blog2epub\\blog2epub_gui.py'],
    pathex=[
        '.',
    ],
    datas=[
        ('./assets/blog2epub_256px.png', '.'),
        ('./assets/blog2epub.png', '.'),
        ('./assets/Alegreya-Regular.ttf', '.'),
        ('./assets/Alegreya-Italic.ttf', '.'),
        ('./assets/MartianMono-Regular.ttf', '.'),
    ],
    hookspath=[],
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    **get_deps_minimal(video=None, audio=None)
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='blog2epub_gui.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=None,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='./assets/blog2epub_256px.png'
)
info_plist = {
    "NSHighResolutionCapable": True,
}
app = BUNDLE(
    exe,
    name='blog2epub_gui.exe',
    icon='./assets/blog2epub.ico',
    bundle_identifier=None,
    info_plist=info_plist
)
