#!/bin/bash
if [ -f "./dist/blog2epub" ]; then
  mkdir -p ./dist/blog2epub.AppDir/usr/bin/
  cp ./dist/blog2epub ./dist/blog2epub.AppDir/usr/bin/
  cp ./assets/blog2epub_256px.png ./dist/blog2epub.AppDir/
  echo """#!/bin/bash
if [[ ! \"\${APPIMAGE}\" || ! \"\${APPDIR}\" ]]; then
  export APPIMAGE=\"\$(readlink -f \"\${0}\")\"
  export APPDIR=\"\$(dirname \"\${APPIMAGE}\")\"
fi
\$APPDIR/usr/bin/blog2epub
""" > ./dist/blog2epub.AppDir/AppRun
  chmod +x ./dist/blog2epub.AppDir/AppRun
  echo """[Desktop Entry]
Name=blog2epub
Exec=blog2epub
Icon=blog2epub_256px
Type=Application
Categories=Utility
Keywords=ebook;epub;ereader;
Terminal=false
StartupNotify=true
NoDisplay=false
""" > ./dist/blog2epub.AppDir/blog2epub.desktop
  ARCH=x86_64 appimagetool-x86_64  ./dist/blog2epub.AppDir ./dist/blog2epub.AppImage
fi