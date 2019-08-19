#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from setuptools import setup

setup(
    name='blog2epub',
    version='1.0.1',
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
        "lxml",
        "Pillow",
        "pycurl",
        "six",
        "python-dateutil",
    ],
    entry_points={
        'console_scripts': [
            'blog2epub = blog2epub.Blog2EpubCli:main'
        ],
        'gui_scripts': [
            'blog2epubqt = blog2epub.Blog2EpubQt:main'
        ]
    },
    package_data={
        'blog2epub': [
            'assets/*.ttf'
        ]
    },
    include_package_data=True,
)
