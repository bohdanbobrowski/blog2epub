# -*- mode: python ; coding: utf-8 -*-
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal

import os
import sys

block_cipher=None
minimal_depts=get_deps_minimal(video=None, audio=None)
minimal_depts["hiddenimports"] += [
    "win32timezone",
    "pytz",
    "imagesize",
    "PIL",
    "kivy",
    "atoma",
    "beautifulsoup4",
    "ebooklib",
    "fake-useragent",
    "filetype",
    "ftfy",
    "imagesize",
    "kivymd",
    "plyer",
    "plyer.platforms.linux.notification",
    "plyer.platforms.linux.filechooser",
    "python-dateutil",
    "pyyaml",
    "strip_tags",
    "webencodings",
]
minimal_depts["excludes"] += [
    "mypy",
    "jnius",
    "coverage",
    "cython",
    "types*",
    "pytest-cov",
]

configuration=Analysis(
    [
        'blog2epub/blog2epub_gui.py'
    ],
    pathex=[
        '.'
    ],
    datas=[
        (os.path.abspath('./assets/blog2epub.svg'), '.'),
        (os.path.abspath('./assets/blog2epub.png'), '.'),
        (os.path.abspath('./assets/blog2epub_256px.png'), '.'),
        (os.path.abspath('./assets/Alegreya-Regular.ttf'), '.'),
        (os.path.abspath('./assets/Alegreya-Italic.ttf'), '.'),
        (os.path.abspath('./assets/LiberationMono-Regular.ttf'), '.'),
    ],
    hookspath=[],
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    **minimal_depts,
)
application_pyz=PYZ(
    configuration.pure,
    configuration.zipped_data,
    cipher=block_cipher
)
application_exe=EXE(
    application_pyz,
    configuration.scripts,
    configuration.binaries,
    configuration.zipfiles,
    configuration.datas,
    name='blog2epub',
    bootloader_ignore_signals=False,
    debug=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/blog2epub.ico',
)
app=BUNDLE(
    application_exe,
    name='blog2epub',
    icon='assets/blog2epub.ico',
    bundle_identifier=None,
    info_plist={'NSHighResolutionCapable': 'True'},
)
