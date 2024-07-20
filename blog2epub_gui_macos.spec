from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [
        'blog2epub/blog2epub_gui.py'
    ],
    pathex=[
        '.'
    ],
    datas=[
        ('./assets/blog2epub.icns', '.'),
        ('./assets/blog2epub_256px.png', '.'),
        ('./assets/blog2epub.png', '.'),
        ('./assets/Alegreya-Regular.ttf', '.'),
        ('./assets/Alegreya-Italic.ttf', '.'),
        ('./assets/MartianMono-Regular.ttf', '.'),
    ],
    hiddenimports=[],
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
    name='blog2epub',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None, 
    icon='blog2epub.icns'
)
info_plist = {
    "NSHighResolutionCapable": True,
}
app = BUNDLE(
    exe,
    name='blog2epub.app',
    icon='assets/blog2epub.icns',
    bundle_identifier=None,
    info_plist=info_plist
)
