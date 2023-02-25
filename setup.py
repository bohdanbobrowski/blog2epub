#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from distutils.core import setup

VERSION = "1.2.1"

setup(
    name="blog2epub",
    version=VERSION,
    description="Blog To Epub Downloader",
    url="https://github.com/bohdanbobrowski/blog2epub",
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
        "six",
        "python-dateutil",
        "atoma",
        "requests",
        "fake-useragent",
        "PyYAML",
        "pycairo",
        "Kivy",
    ],
    entry_points={
        "console_scripts": ["blog2epub = blog2epub.Blog2EpubCli:main"],
        "gui_scripts": ["blog2epubgui = blog2epub.Blog2EpubKivy:main"],
    },
    package_data={"blog2epub": ["assets/*.ttf"]},
    include_package_data=True,
)
