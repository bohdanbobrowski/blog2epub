<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/blog2epub.png" width="128" height="128" />
</p>

# blog2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/blog2epub/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

Convert blog to epub using command line or GUI.

### Supported blogs:
- *.wordpress.com and some blogs based on Wordpress
- *.blogspot.com

### Main features

- command line (CLI) and graphic user interface (GUI)
- script downloads all text contents of selected blog to epub file,
- if it's possible, it includes post comments,
- images are resized (to 400x300px) and converted to grayscale,
- one post = one epub chapter,
- chapters are sorted by date ascending,
- cover is generated automatically from downloaded images.

### Example covers

<table style="width:100%;text-align:center;"><tr><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/cover_1.jpg" width="200" style="margin:0 10px 10px 0" />
</td><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/cover_2.jpg" width="200" style="margin:0 10px 10px 0" />
</td></tr><tr><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/cover_3.jpg" width="200" style="margin:0 10px 10px 0" />
</td><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/cover_4.jpg" width="200" style="margin:0 10px 10px 0;" />
</td></tr></table>

## Installation

- for macOS users: available [app](https://github.com/bohdanbobrowski/blog2epub/releases)
- python3 setup.py install

### Running froum sources

    git clone git@github.com:bohdanbobrowski/blog2epub.git
    cd blog2epub
    python -m venv venv
    source ./venv/bin/activate
    pip install -r ./requirements.txt
    ./blog2epubgui.py

## Screenshots of GUI

### Linux

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/blog2epub_linux_screenshot_v1.2.0.png"  width="500px" />
</p>

### macOS

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/images/blog2epub_osx_screenshot_v1.2.0.png" width="600px" />
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

## TODO list / Planned features

- cross-platform GUI (Kivy)
- macos, linux (and maybe windows) app/package
- mobile app (android)
- more blog engines and templates supported (wordpress.com etc.)

## Release notes

### [1.2.1](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.1)

- Kivy threading fix 

### [1.2.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.0)

- migration to Kivy :-)
- some bugfixes in crawler
- wordpress.com support!

### [1.1.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.1.0)

- migration to Gtk (for better support on multiple platforms)
- requirements cleanup
- about dialog
- macOS dmg installer included

### [1.0.5](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.0.5)

- gzip html in cache folder
- atom feed parsing
- better system notifications, also under linux

### [1.0.4](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.0.4)

- improved saving GUI settings
- system notification on finished download

### [1.0.3](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.0.3)

- saving GUI settings to yaml file
- first macOS builds (pyinstaller)
