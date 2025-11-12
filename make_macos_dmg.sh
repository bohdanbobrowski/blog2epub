#!/bin/bash
if [ -d "./dist/blog2epub.app" ]; then
  mkdir -p ./dist/macos_dng_image/
  cp -r ./dist/blog2epub.app ./dist/macos_dng_image/
  ln -s /Applications ./dist/macos_dng_image/Applications
  hdiutil create /tmp/tmp.dmg -ov -volname "blog2epub" -fs HFS+ -srcfolder "./dist/macos_dng_image/"
  hdiutil convert /tmp/tmp.dmg -format UDZO -o ./dist/blog2epub_v1.5.1_macos.dmg
fi