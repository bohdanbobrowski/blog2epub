<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blogspot2epub/master/images/blog2epub.png" width="128" height="128" />
</p>

# blogspot2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/blogspot2epub/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)


Convert selected blogspot.com blog to epub using single command. After months of struggle, finnally I've uploaded and merged new, deeply refactored version. It is still not perfect and have some bugs... but, hey! I'm still developing it! ;-)

## Main features

- command line (CLI) and graphic user interface (GUI)
- downloads all text contents of selected blog to epub file,
- downloads post comments,
- downloads images, resizes them (to 400x300px) and converts to grayscale,
- one post = one chapter,
- chapters are sorted by date ascending,
- cover is generated automatically

## Installation

- for macOS users: available [app](https://github.com/bohdanbobrowski/blogspot2epub/releases)
- python3 setup.py install

### Running froum sources

    git clone git@github.com:bohdanbobrowski/blogspot2epub.git
    cd blogspot2epub
    python -m venv venv
    source ./venv/bin/activate
    pip install -r ./requirements.txt
    ./blog2epubgui.py

## GUI

### linux

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blogspot2epub/master/images/blog2epub_linux_screenshot.png" />
</p>

### macOS

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blogspot2epub/master/images/blog2epub_osx_screenshot.png" />
</p>

## CLI

    blog2epub [blog url] <parameters>

### Parameters

    -l/--limit=[x] - limit epub file to x posts
    -s/--skip=[x] - skip x latest posts
    -q/--images-quality=[0-100] - included images quality (default is 40)
    -n/--no-images - don't include images

## Examples

    blog2epub starybezpiek.blogspot.com
    blog2epub velosov.blogspot.com -l=10
    blog2epub poznanskiehistorie.blogspot.com -q=100
    blog2epub classicameras.blogspot.com --limit=10 --no-images
    blog2epubgui

## TODO list / Plannned features

- crossplatform GUI (currently under development)
- windows build
- linux build
- mobile app
- more blog engines and templates supported (worpress.com etc.)

## Release notes

### 1.2.0 - IN DEVELOPMENT

- migration to Kivy :-)
- deliver Windows build
- what bout Android app?

### [1.1.0](https://github.com/bohdanbobrowski/blogspot2epub/releases/tag/1.1.0)

- migration to Gtk (for better support on multiple platforms)
- requirements cleanup
- about dialog
- osx dmg installer included

### [1.0.5](https://github.com/bohdanbobrowski/blogspot2epub/releases/tag/1.0.5)

- gzip html in cache folder
- atom feed parsing
- better system notifications, also under linux

### [1.0.4](https://github.com/bohdanbobrowski/blogspot2epub/releases/tag/1.0.4)

- improved saving GUI settings
- system notification on finished download

### [1.0.3](https://github.com/bohdanbobrowski/blogspot2epub/releases/tag/1.0.3)

- saving GUI settings to yaml file
- first macOS builds (--py2app--pyinstaller)