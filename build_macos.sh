#!/bin/bash

rm -rf ./build
rm -rf ./dist
pyinstaller blog2epub_macos.spec
if [ -d "./dist/blog2epub.app" ]; then
  cp -v ./blog2epub/assets/*.ttf ./dist/blog2epub.app/Contents/Resources
  cp -v ./images/blog2epub.png ./dist/blog2epub.app/Contents/Resources
  cp -v ./images/blog2epub.icns ./dist/blog2epub.app/Contents/Resources
  mkdir -p ./dist/osx/
  mv ./dist/blog2epub.app ./dist/osx/
  ln -s /Applications ./dist/osx/Applications
  # ln -s ~/Applications ./dist/osx/Applications
  # mv ./dist/osx/Applications "./dist/osx/ "
  hdiutil create /tmp/tmp.dmg -ov -volname "blog2epub" -fs HFS+ -srcfolder "./dist/osx/"
  hdiutil convert /tmp/tmp.dmg -format UDZO -o ./dist/blog2epub.dmg
fi