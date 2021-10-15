#!/bin/bash

rm -rf ./build
rm -rf ./dist
pyinstaller --onefile --windowed blog2epub_osx.spec
cp -v ./blog2epub/assets/*.ttf ./dist/blog2epub.app/Contents/Resources
cp -v ./images/blog2epub.png ./dist/blog2epub.app/Contents/Resources
cp -v ./images/blog2epub.icns ./dist/blog2epub.app/Contents/Resources