#!/bin/bash

rm -r ./build
rm -r ./dist
pyinstaller blog2epubgui.spec
cp -v ./blog2epub/assets/*.ttf ./dist/blog2epub.app/Contents/MacOS
cp -v ./blog2epub.png ./dist/blog2epub.app/Contents/MacOS