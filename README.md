# blogspot2epub

Convert selected blogspot.com blog to epub using single command. After months of struggle, finnally I've uploaded and merged new, deeply refactored version. It is still not perfect and have some bugs... but, hey! I'm still developing it! ;-)

#### Main features:
- downloads all text contents of selected blog to epub file,
- downloads post comments,
- downloads images, resizes them (to 400x300px) and converts to grayscale,
- one post = one chapter,
- chapters are sorted by date ascending,
- cover is generated automatically

Its still ~~very~~ experimental, but should work... generally.

#### Installation:
- python setup.py install

#### Usage:
- ./blogspot2epub.py [blog-name] <parameters>

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

#### Plannned features:
- crossplatform GUI
- mobile app
- more reliable crawler
- more blog engines and templates supported

**Happy reading! :-)**
