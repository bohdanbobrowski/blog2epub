# -*- mode: python ; coding: utf-8 -*-
from kivy.tools.packaging.pyinstaller_hooks import get_deps_minimal

import os
import sys

block_cipher = None
minimal_depts = get_deps_minimal(video=None, audio=None)
minimal_depts["hiddenimports"] += [
    "win32timezone",
    "pytz",
    "yaml"
    "imagesize",
    "PIL",
    "kivy",
    "atoma",
    "beautifulsoup4",
    "click",
    "ebooklib",
    "fake-useragent",
    "filetype",
    "ftfy",
    "html5lib",
    "imagesize",
    "kivymd",
    "plyer",
    "pyjnius",
    "python-dateutil",
    "pytz",
    "pyyaml",
    "soupsieve",
    "strip_tags",
    "webencodings",
]

configuration = Analysis(
    [
        'blog2epub/blog2epub_gui.py'
    ],
    pathex=[
        '.'
    ],
    datas=[
        (os.path.abspath('./assets/blog2epub.icns'), '.'),
        (os.path.abspath('./assets/blog2epub_256px.png'), '.'),
        (os.path.abspath('./assets/blog2epub.png'), '.'),
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
application_pyz = PYZ(
    configuration.pure,
    configuration.zipped_data,
    cipher=block_cipher
)
application_exe = EXE(
    application_pyz,
    configuration.scripts,
    configuration.binaries,
    configuration.zipfiles,
    configuration.datas,
    name = 'blog2epub',
    debug = False,
    strip = False,
    upx = True,
    runtime_tmpdir = None,
    console = False,
)
app = BUNDLE(
    application_exe,
    name='blog2epub.app',
    icon='assets/blog2epub.icns',
    bundle_identifier=None,
    info_plist = {'NSHighResolutionCapable': 'True'},
)
