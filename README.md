# blogspot2epub
Convert selected webpage to epub using single command!

Script is compatible with:
- blogspot.com
- pulshistorii.pb.pl

Main features:
- downloads all text contents of selected blog to epub file,
- downloads post comments,
- downloads images, resizes them (to 800x600px) and converts to grayscale,
- one post = one chapter,
- chapters are sorted by date ascending,
- optional: it adds cover, if you add jpg file with the same name like blog you want to download (sample.jpg for sample.blogspot.com),

Its still very experimental, but should work... generally.

Usage:
- ./blogspot2epub.py [blog-name]
- ./pulshistorii2epub.py [tag-id]

Examples:
- ./blogspot2epub.py starybezpiek
- ./blogspot2epub.py poznanskiehistorie
- ./pulshistorii2epub.py 36169

Happy reading!
:-)
