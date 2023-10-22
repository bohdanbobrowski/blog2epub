# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['blog2epubkivy.py'],
             pathex=[
                './venv/',
             ],
             binaries=[],
             datas=[
                ('./images/blog2epub_256px.png', '.'),
                ('./images/blog2epub.png', '.'),
                ('./assets/Lato-Bold.ttf', '.'),
                ('./assets/Lato-Italic.ttf', '.'),
                ('./assets/Lato-Regular.ttf', '.'),
             ],
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
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='blog2epub.exe',
          debug=False,
          bootloader_ignore_signals=False,
          strip=None,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='./images/blog2epub_256px.png')
info_plist = {
    "NSHighResolutionCapable": True,
}
app = BUNDLE(exe,
             name='blog2epub.exe',
             icon='./images/blog2epub.ico',
             bundle_identifier=None,
             info_plist=info_plist)
