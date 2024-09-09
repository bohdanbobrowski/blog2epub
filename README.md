<p align="center">
<img src="./assets/blog2epub_256px.png" width="256" height="256" />
</p>

# blog2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/blog2epub/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/) ![GitHub all releases](https://img.shields.io/github/downloads/bohdanbobrowski/blog2epub/total) ![GitHub release (with filter)](https://img.shields.io/github/v/release/bohdanbobrowski/blog2epub) ![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/bohdanbobrowski/blog2epub)

Convert blog to epub using command line or GUI.

### Supported blogs:
- *.blogspot.com
- *.wordpress.com and some blogs based on WordPress

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
<img src="assets/v1.3.0/knippsen.blogspot.com_2023.04.01-2024.05.20.epub.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="assets/v1.3.0/rocket-garage.blogspot.com_2024.01.21-2024.06.16.epub.jpg" width="400" style="margin:0 10px 10px 0" />
</td></tr><tr><td>
<img src="assets/v1.3.0/starybezpiek.blogspot.com_2014.11.04-2015.12.15.epub.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="assets/v1.3.0/velosov.blogspot.com_2013.02.02-2013.03.10.epub.jpg" width="400" style="margin:0 10px 10px 0;" />
</td></tr></table>

## Installation

Checkout for latest available [builds](https://github.com/bohdanbobrowski/blog2epub/releases).

### Running from sources

    git clone git@github.com:bohdanbobrowski/blog2epub.git
    cd blog2epub
    poetry install
    poetry run blog2epubgui

### Building own executable

#### Windows

    poetry run build_gui_windows

#### macOS

    poetry run build_gui_macos

And then to create dmg image with app:

    ./make_macos_dmg.sh

## Screenshots of GUI

### Windows (11)

<p align="center">
<img src="assets/v1.3.0/blog2epub_win11_screenshot.png" width="600px" />
</p>

### Linux (Manjaro Gnome)

<p align="center">
<img src="assets/v1.3.0/blog2epub_linux_screenshot.png"  width="600px" />
</p>

### macOS (Sonoma 14.4.1)

<p align="center">
<img src="assets/v1.3.0/blog2epub_macos_screenshot.png"  width="600px" />
</p>

### Android (Google Pixel 6a)

<p align="center">
<img src="assets/v1.4.0/blog2pub_android_pixel6a_screenshot1.png"  width="200px" />
<img src="assets/v1.4.0/blog2pub_android_pixel6a_screenshot2.png"  width="200px" />
<img src="assets/v1.4.0/blog2pub_android_pixel6a_screenshot3.png"  width="200px" />
<img src="assets/v1.4.0/blog2pub_android_pixel6a_screenshot4.png"  width="200px" />
</p>

## CLI

    poetry run blog2epub [blog url] <parameters>

### Parameters

    -l/--limit=[x] - limit epub file to x posts
    -s/--skip=[x] - skip x latest posts
    -q/--images-quality=[0-100] - included images quality (default is 40)
    -n/--no-images - don't include images

## Examples

    poetry run blog2epub starybezpiek.blogspot.com
    poetry run blog2epub velosov.blogspot.com -l=10
    poetry run blog2epub poznanskiehistorie.blogspot.com -q=100
    poetry run blog2epub classicameras.blogspot.com --limit=10 --no-images

## Current version

### [v1.4.0]
- [X] custom destination folder
- [X] UI improvements (better scaling, more rely on KivyMD default features)
- [X] mypy and ruff pipeline job (via github Actions)
- [X] Android build
- [ ] unit testing - at least for some part of the code
- [ ] crawlers refactor - some part is done
- [ ] fix minor Android bugs


[&raquo; Complete Change Log here &laquo;](https://github.com/bohdanbobrowski/blog2epub/blob/master/CHANGELOG.md)

## Project backlog

And finally, a list known bugs and future plans for some new functions and enhancements: [BACKLOG.md](https://github.com/bohdanbobrowski/blog2epub/blob/master/BACKLOG.md)