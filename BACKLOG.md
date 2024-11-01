# List of features and bugfixes I'm considering to add

## Known bugs
- [ ] sometimes images are not correctly scrapped and replaced, like in this post: [modernistyczny-poznan.blogspot.com](https://modernistyczny-poznan.blogspot.com/2021/08/wiepofama-10lat.html)
- [ ] app is not resistant to http errors, which is embarrassing

## Scraping in general:
- [ ] stop with keeping content in RAM - save it as ready to use ebook chapters
- [ ] use sitemaps.xml for scraping!
- [ ] replace blog url's in article content to actual chapters in ebook
- [ ] major refactor of Crawler class:
  - [ ] use data models
  - [ ] more common methods in crawler class
  - [ ] expand crawler abstract
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
- [ ] [zeissikonveb.de](zeissikonveb.de)
- [ ] [scigacz.pl](https://www.scigacz.pl/)
- [ ] [jednoslad.pl](https://www.jednoslad.pl)
