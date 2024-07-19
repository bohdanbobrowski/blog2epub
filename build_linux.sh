#!/bin/bash

rm -rf ./build
rm -rf ./dist
pyinstaller blog2epub_gui_linux.spec
cp -v ./blog2epub/assets/*.ttf ./dist/
cp -v ./images/blog2epub.svg ./dist/
cp -v ./images/blog2epub.png ./dist/
cp -v ./images/blog2epub.icns ./dist/
cd ./dist/
export PWD=`pwd`
export B2EPATH="$PWD/blog2epub"
gendesk -f --pkgname="blog2epub" --pkgdesc="Blog To Epub Downloader" --icon="$B2EPATH.icns" --exec="$B2EPATH"
cd ..
chmod +x ${B2EPATH}.desktop
desktop-file-validate ${B2EPATH}.desktop