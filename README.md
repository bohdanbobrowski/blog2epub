<p align="center">
<img src="./assets/blog2epub_256px.png" width="256" height="256" />
</p>

# blog2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/blog2epub/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

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
<img src="./assets/blog2epub_win10_screenshot.png" width="600px" />
</p>

### macOS

<p align="center">
<img src="./assets/blog2epub_macos_screenshot.png" width="600px" />
</p>

### Linux

Mint 21.2 Cinnamon

<p align="center">
<img src="./assets/blog2epub_linux_screenshot.png"  width="600px" />
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

## Planned features and known bugs

- [ ] code needs some refactor: classes are too "nested" within each other
- [ ] there are some bugs in wordpress.com crawler
- [ ] Linux app/package(s)
- [ ] Android app
- [ ] more crawlers (ex. GitHub Pages 🙃)
- [ ] improve existing crawlers (allow)
- [ ] improve GUI - configuration, allow to save in selected place etc.
- [ ] utilize GitHub Pages for this project documentation

## Current release

### [v1.2.5](#in-development) - Unreleased
- [x] save url textfield history and allow easily choose from these urls
- [x] change font from Lato (nice but large files) to much smaller ([Alegreya](https://github.com/huertatipografica/Alegreya) and [Martian Mono](https://github.com/evilmartians/mono) for UI)
- [x] make program window not resizable
- [x] add popup similar to about dialog after finished ebook generation

### [v1.2.4](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.4) - 2023-10-25
- [x] article loop fix (crawler was reading by default from atomfeed, and returning maximum 25 articles)
- [x] refactor, as usual
- [x] url history saved into yaml file