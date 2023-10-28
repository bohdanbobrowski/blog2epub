## Release notes

### [1.2.5](#in-development)
- [ ] utilize GitHub Pages for this project documentation
- [x] save url textfield history and allow easily choose from these urls
- [x] change font from Lato (nice but large files) to much smaller ([Alegreya](https://github.com/huertatipografica/Alegreya) and [Martian Mono](https://github.com/evilmartians/mono) for UI)
- [x] make program window not resizable
- [x] add popup similar to about dialog after finished ebook generation

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
