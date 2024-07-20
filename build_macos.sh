#!/bin/bash
if [ -d "./dist/blog2epub.app" ]; then
  if [ -d "./dist/macos_dng_image" ]; then
    rm -r "./dist/macos_dng_image"
  fi
  # TODO: investigate why these 4 files were not copied to app
  cp -v ./assets/Alegreya-Regular.ttf ./dist/blog2epub.app/Contents/Resources
  cp -v ./assets/Alegreya-Italic.ttf ./dist/blog2epub.app/Contents/Resources
  cp -v ./assets/MartianMono-Regular.ttf ./dist/blog2epub.app/Contents/Resources
  cp -v ./assets/blog2epub.png ./dist/blog2epub.app/Contents/Resources
  mkdir -p ./dist/macos_dng_image/
  cp -r ./dist/blog2epub.app ./dist/macos_dng_image/
  ln -s /Applications ./dist/macos_dng_image/Applications
  # ln -s ~/Applications ./dist/macos_dng_image/Applications
  # mv ./dist/macos_dng_image/Applications "./dist/macos_dng_image/ "
  hdiutil create /tmp/tmp.dmg -ov -volname "blog2epub" -fs HFS+ -srcfolder "./dist/macos_dng_image/"
  hdiutil convert /tmp/tmp.dmg -format UDZO -o ./dist/blog2epub.dmg
fi