#!/bin/bash
if [ -f "./dist/blog2epub" ]; then
  mkdir -p ./dist/blog2epub_v1.5.0.AppDir/usr/bin/
  cp ./dist/blog2epub ./dist/blog2epub_v1.5.0.AppDir/usr/bin/
  cp ./assets/blog2epub.svg ./dist/blog2epub_v1.5.0.AppDir/
  echo """#!/bin/bash
if [[ ! \"\${APPIMAGE}\" || ! \"\${APPDIR}\" ]]; then
  export APPIMAGE=\"\$(readlink -f \"\${0}\")\"
  export APPDIR=\"\$(dirname \"\${APPIMAGE}\")\"
fi
\$APPDIR/usr/bin/blog2epub
""" > ./dist/blog2epub_v1.5.0.AppDir/AppRun
  chmod +x ./dist/blog2epub_v1.5.0.AppDir/AppRun
  echo """[Desktop Entry]
Name=blog2epub
Exec=blog2epub
Icon=blog2epub
Type=Application
Categories=Utility
Keywords=ebook;epub;ereader;
Terminal=false
StartupNotify=true
NoDisplay=false
""" > ./dist/blog2epub_v1.5.0.AppDir/blog2epub.desktop
  ARCH=x86_64 appimagetool-x86_64  ./dist/blog2epub_v1.5.0.AppDir ./dist/blog2epub_v1.5.0.AppImage
fi