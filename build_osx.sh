#!/bin/bash

rm -r ./build
rm -r ./dist
pyinstaller blog2epubgui.spec
cp ./blog2epub/assets/*.ttf ./dist/blog2epub.app/Contents/MacOS