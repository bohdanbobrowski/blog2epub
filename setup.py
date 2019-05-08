#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from setuptools import setup

setup(
    name='blog2epub',
    version='0.3',
    description="Blog To Epub Downloader",
    url="https://github.com/bohdanbobrowski/blogspot2epub",
    author="Bohdan Bobrowski",
    author_email="bohdanbobrowski@gmail.com",
    license="MIT",
    packages=[
        "blog2epub"
    ],
    install_requires=[
        "eyed3",
        "mutagen",
        "slugify",
        "pycurl",
        "pillow",
        "clint"
    ],
    entry_points={
        'console_scripts': [
            'blog2epub = blog2epub.blog2epub-cli:main'
        ],
    },
    package_data={
        'prdl': [
            '*.jpg'
        ]
    },
    include_package_data = True,
)
