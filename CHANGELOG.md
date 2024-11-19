# ChangeLog

### v1.5.0
- [X] integration testing
- [X] increase unit test coverage
- [X] use sitemaps.xml for scraping
- [X] crawlers refactor
  - [X] use data models
  - [X] more common methods in crawler class
  - [X] expand crawler abstract
- [X] cli interface refactor
- [X] greek alphabet support
- [X] image download and attachment bug solved (ex. modernistyczny-poznan.blogspot.com)
- [X] improved resistance to http errors
- [X] dedicated crawler class for zeissikonveb.de

### [v1.4.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.4.0) - 2024-11-01
- [X] custom destination folder
- [X] UI improvements (better scaling, more rely on KivyMD default features)
- [X] mypy and ruff pipeline job (via github Actions)
- [X] Android build
- [X] begin unit testing
- [X] crawlers refactor - some part is done

### [v1.3.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.3.0) - 2024-07-20
- [X] introduce KivyMD
- [X] python poetry instead of venv
- [X] code refactor and cleanup
- [X] add tabbed layout with list of articles
- [X] 2 stages: crawl/download & ebook generation
- [X] selectable list of articles
- [X] feature: prevent epub file overwriting
- [X] feature: cancel download
- [X] fixed bug: chapters were not added to ebook spine, which caused problems with navigation
- [X] Windows and macOS builds

### [v1.2.6](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.6) - 2024-03-30
- [x] resistance to broken links
- [x] atom feed when skipped
- [x] better comments support
- [x] more random cover generator
 
### [v1.2.5](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.5) - 2023-10-30
- [x] save url textfield history and allow easily choose from these urls
- [x] change font from Lato (nice but large files) to much smaller ([Alegreya](https://github.com/huertatipografica/Alegreya) and [Martian Mono](https://github.com/evilmartians/mono) for UI)
- [x] make program window not resizable
- [x] add popup similar to about dialog after finished ebook generation

### [v1.2.4](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.4) - 2023-10-25
- [x] article loop fix (crawler was reading by default from atomfeed, and returning maximum 25 articles)
- [x] refactor, as usual
- [x] url history saved into yaml file

### [v1.2.3](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.3) - 2023-10-22
- [x] Windows and macOS (unsigned) builds
- [x] fixed encoding error in month name
- [x] some minor refactors and fixes

### [v1.2.2](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.2) - 2023-10-19
- [x] Empty images list bug
- [x] Fixing macOS build (works on my machine - Ventura 13.3.1)
- [x] Improving macOS build - dmg now contains Applications folder shortcut to ease installation

### [v1.2.1](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.1) - 2022-10-21
- [x] Kivy threading fix
- [x] skip parameter fix
- [x] Linux build (now I'm working on adding package to various linux package repositories)

### [v1.2.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.2.0) - 2022-10-06
- [x] migration to Kivy :-)
- [x] some bugfixes in crawler
- [x] wordpress.com support!

### [v1.1.0](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.1.0) - 2021-10-08
- [x] migration to Gtk (for better support on multiple platforms)
- [x] requirements cleanup
- [x] about dialog
- [x] macOS dmg installer included

### [v1.0.5](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.0.5) - 2019-10-25
- [x] gzip html in cache folder
- [x] atom feed parsing
- [x] better system notifications, also under linux

### [v1.0.4](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.0.4) - 2019-08-24
- [x] improved saving GUI settings
- [x] system notification on finished download

### [v1.0.3](https://github.com/bohdanbobrowski/blog2epub/releases/tag/v1.0.3) - 2019-08-23

- [x] saving GUI settings to yaml file
- [x] first macOS builds (pyinstaller)

