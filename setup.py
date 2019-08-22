#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from setuptools import setup

VERSION = '1.0.3'
APP = ['blog2epubgui.py']
DATA_FILES = [
    'blog2epub/assets/Lato-Bold.ttf',
    'blog2epub/assets/Lato-Italic.ttf',
    'blog2epub/assets/Lato-Regular.ttf',
]
OPTIONS = {
    'iconfile':'blog2epub.icns',
    'plist': {
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
    },
    'includes': [
        'lxml', 'beautifulsoup4', 'Pillow', 'os', 'platform', 'tkinter'
    ],
    'argv_emulation': False
}

setup(
    name='blog2epub',
    app=APP,
    version=VERSION,
    description="Blog To Epub Downloader",
    url="https://github.com/bohdanbobrowski/blogspot2epub",
    author="Bohdan Bobrowski",
    author_email="bohdanbobrowski@gmail.com",
    license="MIT",
    packages=[
        "blog2epub",
        "blog2epub.crawlers",
    ],
    install_requires=[
        "EbookLib",
        "beautifulsoup4",
        "lxml",
        "Pillow",
        "pycurl",
        "six",
        "python-dateutil",
    ],
    data_files=DATA_FILES,
    options={
        'py2app': OPTIONS
    },
    setup_requires=['py2app'],
    entry_points={
        'console_scripts': [
            'blog2epub = blog2epub.Blog2EpubCli:main'
        ],
        'gui_scripts': [
            'blog2epubgui = blog2epub.Blog2EpubGui:main'
        ]
    },
    package_data={
        'blog2epub': [
            'assets/*.ttf'
        ]
    },
    include_package_data=True,
)
