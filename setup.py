#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from distutils.core import setup

from blog2epub.common.globals import VERSION

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
        "pydantic",
        "beautifulsoup4",
        "ebooklib",
        "python-dateutil",
        "atoma",
        "fake-useragent",
        "pyyaml",
        "pycairo",
        "kivy",
        "kivymd",
    ],
    entry_points={
        "console_scripts": ["blog2epub = blog2epub.blog2epub_cli:main"],
        "gui_scripts": ["blog2epubgui = blog2epub.blog2epub_kivy:main"],
    },
    package_data={"blog2epub": ["assets/*.ttf"]},
    include_package_data=True,
)
