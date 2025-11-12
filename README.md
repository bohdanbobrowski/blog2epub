<p align="center">
<img src="./assets/blog2epub_256px.png" width="256" height="256" />
</p>

# blog2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/blog2epub/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/) ![GitHub all releases](https://img.shields.io/github/downloads/bohdanbobrowski/blog2epub/total) ![GitHub release (with filter)](https://img.shields.io/github/v/release/bohdanbobrowski/blog2epub) ![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/bohdanbobrowski/blog2epub)

<a href="https://apps.microsoft.com/detail/XP9M0FG8NP0N8K?mode=direct">
	<img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>
<a href="#">
	<img src="./assets/download-appimage-banner.svg" width="200"/>
</a>

Convert website (blog) to epub using command line or GUI.

> My main goal in creating this app is to preserve the legacy of the blogosphere for future generations.

### Supported blogs:
- *.blogspot.com
- *.wordpress.com
- multiple other blogs and even some webpages

### Main features

- command line (CLI) and graphic user interface (GUI)
- script downloads all text contents of selected blog to epub file,
- if it's possible, it includes post comments,
- images are downsized to given resolution (`600*800`,`640*960` or `1236*1648`)
- images are also by default converted to grayscale,
- one post = one epub chapter,
- chapters are sorted by date ascending,
- cover is generated automatically from downloaded images.

### Example covers

<table style="width:100%;text-align:center;"><tr><td>
<img src="assets/v1.5.0/zeissikonveb_de_2023.11.17-2025.06.07.epub.jpg" width="400" style="margin:0 10px 10px 0;" />
</td><td>
<img src="assets/v1.5.0/starybezpiek_blogspot_com_2014.11.04-2015.12.15.epub.jpg" width="400" style="margin:0 10px 10px 0;" />
</td></tr><tr><td>
<img src="assets/v1.5.0/magazynbiomasa_pl_2025.10.24-2025.11.01.epub.jpg" width="400" style="margin:0 10px 10px 0;" />
</td><td>
<img src="assets/v1.5.0/boston1775_blogspot_com_2024.11.10-2024.11.14.epub.jpg" width="400" style="margin:0 10px 10px 0" />
</td></tr><tr><td>
<img src="assets/v1.5.0/velosov_blogspot_com_2013.02.22-2013.03.10.epub.jpg" width="400" style="margin:0 10px 10px 0" />
</td><td>
<img src="assets/v1.5.0/archaia-ellada_blogspot_com_2014.11.01-2014.12.01.epub.jpg" width="400" style="margin:0 10px 10px 0" />
</td></tr></table>

## Installation

Checkout for latest available [builds](https://github.com/bohdanbobrowski/blog2epub/releases).

### Running from sources

#### Easiest way

    pip install git+https://github.com/bohdanbobrowski/blog2epub.git

#### Developer environment

    git clone git@github.com:bohdanbobrowski/blog2epub.git
    cd blog2epub
    python -m venv venv 

##### Windows:
    venv\Scripts\activate
    pip install -e .[dev]
    
#### macOS/Linux:

    source ./venv/bin/activate
    pip install -e .[dev]

### Building own executable

Build environment should contain only what is necessary to prepare build:

    pip install .
    pip instal pyinstaller

#### Android

    buildozer android debug

#### Windows

    python build_windows.py
    "C:\Program Files (x86)\NSIS\makensis" blog2epub_windows_installer.nsi

#### macOS

    python build_macos.py
    ./make_macos_dmg.sh

#### Linux

I love Linux, but this gives me a headache:

###### AppImage

Works fine, but is HUGE (about 250 MB).

    python build_linux.py
    ./make_linux_appimage.sh

###### Snap

This is promising, despite taking 150 MB... but still i have issues with `plyer` modules called `fileselect` and `notification`.

    snapcraft pack

## Screenshots of GUI

### Android (Google Pixel 6a)

<p align="center">
<img src="assets/v1.5.0/blog2pub_android_pixel6_screenshot1.png"  width="200px" />
<img src="assets/v1.5.0/blog2pub_android_pixel6_screenshot2.png"  width="200px" />
<img src="assets/v1.5.0/blog2pub_android_pixel6_screenshot3.png"  width="200px" />
<img src="assets/v1.5.0/blog2pub_android_pixel6_screenshot4.png"  width="200px" />
<img src="assets/v1.5.0/blog2pub_android_pixel6_screenshot5.png"  width="200px" />
<img src="assets/v1.5.0/blog2pub_android_pixel6_screenshot6.png"  width="200px" />
</p>

### Windows (11)

<p align="center">
<img src="assets/v1.5.0/blog2epub_win11_screenshot.png" width="600px" />
</p>

### Linux (Ubuntu 24.04)

<p align="center">
<img src="assets/v1.5.0/blog2epub_linux_screenshot.png"  width="600px" />
</p>

### macOS (Sequoia  15.6)

<p align="center">
<img src="assets/v1.5.0/blog2epub_macos_screenshot.png"  width="600px" />
</p>

## CLI

    blog2epub --help
    usage: Blog2epub Cli interface [-h] [-l LIMIT] [-s SKIP] [-q QUALITY] [-o OUTPUT] [-d] url
    
    Convert blog (blogspot.com, wordpress.com or another based on Wordpress) to epub using CLI or GUI.
    
    positional arguments:
      url                   url of blog to download
    
    options:
      -h, --help            show this help message and exit
      -l LIMIT, --limit LIMIT
                            articles limit
      -s SKIP, --skip SKIP  number of skipped articles
      -q QUALITY, --quality QUALITY
                            images quality (0-100)
      -o OUTPUT, --output OUTPUT
                            output epub file name
      -d, --debug           turn on debug

Example:

    blog2epub starybezpiek.blogspot.com -l=2 -o=example.epub
    Starting blogger.com crawler
    Found 54 articles to crawl.
    Downloading.
    1. 10 lat kremlowskiej propagandy, czyli RT ujawnia swoje sekrety
    Downloading.
    2. "Komunę obaliliśmy, a nadal jest źle. Dlaczego?" Czyli 1984 Orwella właściwie odczytany
    Locale set as en_US.UTF-8
    Generating cover (800px*600px) from 1 images.
    Cover generated: .\starybezpiek.blogspot.com\example.epub.jpg
    Epub created: .\example.epub

## Examples

    blog2epub starybezpiek.blogspot.com
    blog2epub velosov.blogspot.com -l=10
    blog2epub poznanskiehistorie.blogspot.com -q=100
    blog2epub classicameras.blogspot.com --limit=10 --no-images

## Running tests

    pytest ./tests
    pytest --cov=blog2epub ./tests
    pytest --cov=blog2epub --cov-report=html ./tests


## Current version

### [v1.5.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.5.0)
- [X] integration testing
- [X] increase unit test coverage
- [X] use sitemaps.xml for scraping
- [X] crawlers refactor
  - [X] use builtin dataclasses instead of pydantic
  - [X] more common methods in crawler class
  - [X] expand crawler abstract
- [X] cli interface refactor
- [X] greek alphabet support
- [X] image download and attachment bug solved (ex. modernistyczny-poznan.blogspot.com)
- [X] color/bw images and covers
- [X] custom image/cover sizes
- [X] improved resistance to http errors
- [X] dedicated crawler class for zeissikonveb.de
- [X] (on GUI) skip value is enlarged on limit value (if such is set)
- [X] download progress is much more verbose, also on GUI it can be cancelled everytime
- [X] remove poetry as it's overcomplicated for the case, 
- [X] results of cancelled downloads might be converted to epub
- [X] Android version
- [X] Windows installer (published on Microsoft Store)
- [X] Linux packages: Appimage and Snap (still experimental)
- [X] GitHub actions builds for macOS, Windows and Linux

[&raquo; Complete Change Log here &laquo;](https://github.com/bohdanbobrowski/blog2epub/blob/master/CHANGELOG.md)

## Project backlog

And finally, a list known bugs and future plans for some new functions and enhancements: [BACKLOG.md](https://github.com/bohdanbobrowski/blog2epub/blob/master/BACKLOG.md)

## Project road map:

- 1.0 - somewhat working
- 2.0 - fully working project, 90% unit tested and available builds for Android/Windows/Linux/MacOS
