<p align="center">
<img src="/assets/blog2epub_256px.png" width="256" height="256" />
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

## CLI

    blog2epub [blog url] <parameters>

#### Parameters

    -l/--limit=[x] - limit epub file to x posts
    -s/--skip=[x] - skip x latest posts
    -q/--images-quality=[0-100] - included images quality (default is 40)
    -n/--no-images - don't include images

#### Examples

    blog2epub starybezpiek.blogspot.com
    blog2epub velosov.blogspot.com -l=10
    blog2epub poznanskiehistorie.blogspot.com -q=100
    blog2epub classicameras.blogspot.com --limit=10 --no-images

