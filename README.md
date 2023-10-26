<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/blog2epub_256px.png" width="256" height="256" />
</p>

# blog2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/blog2epub/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

Convert blog to epub using command line or GUI.

### Supported blogs:
- *.wordpress.com and some blogs based on WordPress
- *.blogspot.com

### Main features

- command line (CLI) and graphic user interface (GUI)
- script downloads all text contents of selected blog to epub file,
- if it's possible, it includes post comments,
- images are downsized (to maximum 800/600px) and converted to grayscale,
- one post = one epub chapter,
- chapters are sorted by date ascending,
- cover is generated automatically from downloaded images.

### Example covers

<table style="width:100%;text-align:center;"><tr><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/cover_1.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/cover_2.jpg" width="400" style="margin:0 10px 10px 0" />
</td></tr><tr><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/cover_3.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/cover_4.jpg" width="400" style="margin:0 10px 10px 0;" />
</td></tr></table>

## Installation

- for Windows and macOS users: available [builds](https://github.com/bohdanbobrowski/blog2epub/releases)
- python3 setup.py install

### Running froum sources

    git clone git@github.com:bohdanbobrowski/blog2epub.git
    cd blog2epub
    python -m venv venv
    source ./venv/bin/activate
    pip install -r ./requirements.txt
    ./blog2epubgui.py

## Screenshots of GUI

### Windows 10

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/blog2epub_win10_screenshot.png" width="600px" />
</p>

### macOS

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/blog2epub_macos_screenshot.png" width="600px" />
</p>

### Linux

<p align="center">
<img src="https://raw.githubusercontent.com/bohdanbobrowski/blog2epub/master/assets/blog2epub_linux_screenshot.png"  width="600px" />
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

- code needs some refactor: classes are too "nested" within each other
- Windows, linux app/package
- mobile app (but rather only Android)
- more blog engines and templates supported (wordpress.com etc.)

## Release notes

### [1.2.4](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.4)

- article loop fix (crawler was reading by default from atomfeed, and returning maximum 25 articles)
- refactor, as usual
- url history saved into yaml file

### [1.2.3](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.3)

- Windows and macOS (unsigned) builds
- fixed encoding error in month name
- some minor refactors and fixes

### [1.2.2](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.2)

- Empty images list bug
- Fixing macOS build (works on my machine - Ventura 13.3.1)
- Improving macOS build - dmg now contains Applications folder shortcut to ease installation

### [1.2.1](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.1)

- Kivy threading fix
- skip parameter fix
- Linux build (now I'm working on adding package to various linux package repositories)

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
