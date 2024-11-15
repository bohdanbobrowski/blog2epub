# List of features and bugfixes I'm considering to add

## Known bugs
..

## Scraping in general:
- [ ] stop with keeping content in RAM - save it as ready to use ebook chapters
- [ ] replace blog internal url's in article content to actual chapters in ebook
- [ ] support for blog categories, tags and pages
- [ ] manually decide which crawler should be used
- [ ] blog2epub.yaml - this might be too ambitious, but what if user could compose he's/hers own book, with custom
  cover, metadata and which contain articles from different blogs and websites around the web? A dockerfile.yaml for
  ebooks.

## GUI, CLI and app distribution
- [ ] fix bloody macOS build! - it build but app misses some assets, and what worse it does not run on any other machine
  (which means *.app is broken)
- [ ] add some linux packages: aur looks promising, and dmg aswell - what about Flatpak, Snap and Appimage?

## Additional crawlers:
- [ ] [nrdblog.cmosnet.eu](https://nrdblog.cmosnet.eu/)
- [ ] [scigacz.pl](https://www.scigacz.pl/)
- [ ] [jednoslad.pl](https://www.jednoslad.pl)
