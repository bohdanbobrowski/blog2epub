# blogspot2epub

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)


Convert selected blogspot.com blog to epub using single command. After months of struggle, finnally I've uploaded and merged new, deeply refactored version. It is still not perfect and have some bugs... but, hey! I'm still developing it! ;-)

#### Main features:
- downloads all text contents of selected blog to epub file,
- downloads post comments,
- downloads images, resizes them (to 400x300px) and converts to grayscale,
- one post = one chapter,
- chapters are sorted by date ascending,
- cover is generated automatically

#### Installation:
- python3 setup.py install

#### Usage:
- blog2epub [blog url] <parameters>

##### Parameters:
- -l/--limit=[x] - limit epub file to x posts
- -s/--skip=[x] - skip x latest posts
- -q/--images-quality=[0-100] - included images quality (default is 40)
- -n/--no-images - don't include images

##### Examples:
- blog2epub starybezpiek.blogspot.com
- blog2epub starybezpiek.blogspot.com -l=10
- blog2epub poznanskiehistorie.blogspot.com
- blog2epub poznanskiehistorie.blogspot.com -q=100
- blog2epub poznanskiehistorie.blogspot.com --limit=10 --no-images
- blog2epubgui

#### Plannned features:
- crossplatform GUI (currently under development)
- mobile app
- more blog engines and templates supported

## Release notes

### [![GitHub release](https://img.shields.io/github/release/Naereen/StrapDown.js.svg)](https://github.com/bohdanbobrowski/blogspot2epub/releases/tag/1.0.1)
- first stable release
- only CLI 