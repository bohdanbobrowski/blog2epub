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
<img src="./assets/cover_1.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="./assets/cover_2.jpg" width="400" style="margin:0 10px 10px 0" />
</td></tr><tr><td>
<img src="./assets/cover_3.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="./assets/cover_4.jpg" width="400" style="margin:0 10px 10px 0;" />
</td></tr></table>

## Installation

- for __Windows__ and __macOS__ users: available [builds](https://github.com/bohdanbobrowski/blog2epub/releases)
- python3 setup.py install

### Running from sources

    git clone git@github.com:bohdanbobrowski/blog2epub.git
    cd blog2epub
    poetry install
    poetry run blog2epubgui

### Building own executable

#### Windows

    poetry run build_gui_windows

## Screenshots of GUI

### Windows (11)

<p align="center">
<img src="./assets/blog2epub_win11_screenshot.png" width="600px" />
</p>

### Linux (Manjaro Gnome)

<p align="center">
<img src="./assets/blog2epub_linux_screenshot.png"  width="600px" />
</p>

### macOS

*TO DO*

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

## Planned features and known bugs

- [ ] Linux app/package(s)
- [ ] Android app
- [ ] code needs still refactor
- [ ] more crawlers
- [ ] improve GUI - configuration, allow to save in selected place etc.
- [ ] save downloaded page structure to yaml file

## Change Log

### [v1.3.0](#v1.3.0) - release will be published soon

- [X] introduce KivyMD
- [X] python poetry instead of venv
- [X] code refactor and cleanup
- [X] add tabbed layout with list of articles
- [X] 2 stages: crawl/download & ebook generation
- [X] selectable list of articles
- [X] feature: prevent epub file overwriting
- [X] feature: cancel download
- [X] fixed bug: chapters were not added to ebook spine, which caused problems with navigation
- [X] windows build

Still TODO in this version:
- [ ] feature: change epub file destination
- [ ] update documentation and screenshots!
- [ ] linux build - FLATPAK?
- [ ] osx build???

[&raquo; Complete Change Log here &laquo;](https://github.com/bohdanbobrowski/blog2epub/blob/master/CHANGELOG.md)