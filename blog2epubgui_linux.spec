# -*- mode: python ; coding: utf-8 -*-
options = [ ('v', None, 'OPTION')]
block_cipher = None

a = Analysis(
    [
        'blog2epubkivy.py'
    ],
    pathex=[
        './venv/'    
    ],
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
    runtime_tmpdir=None,
    console=False
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None, 
    icon='blog2epub.icns'   
)
