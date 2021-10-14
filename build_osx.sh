#!/bin/bash

rm -rf ./build
rm -rf ./dist
pyinstaller --onefile --windowed blog2epubgui_osx.spec
cp -v ./blog2epub/assets/*.ttf ./dist/blog2epub.app/Contents/MacOS
cp -v ./images/blog2epub.png ./dist/blog2epub.app/Contents/MacOS