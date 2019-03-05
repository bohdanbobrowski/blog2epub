# blogspot2epub

## Warning: this branch is currently during deep refactor

Convert selected blogspot blog to epub using single command!

Main features:
- downloads all text contents of selected blog to epub file,
- downloads post comments,
- downloads images, resizes them (to 400x300px) and converts to grayscale,
- one post = one chapter,
- chapters are sorted by date ascending,
- cover is generated automatically

Its still very experimental, but should work... generally.

Usage:
- ./blogspot2epub.py [blog-name] <parameters>

Parameters:
- -l/--limit=[x] - limit epub file to x posts
- -s/--skip=[x] - skip x latest posts
- -q/--images-quality=[0-100] - included images quality (default is 40)
- -n/--no-images - don't include images

Examples:
- ./blogspot2epub.py starybezpiek
- ./blogspot2epub.py starybezpiek -l=10
- ./blogspot2epub.py poznanskiehistorie
- ./blogspot2epub.py poznanskiehistorie -q=100
- ./blogspot2epub.py poznanskiehistorie --limit=10 --no-images
- ./blogspot2epub.py jabolowaballada -l=10 -n

Happy reading!
:-)
