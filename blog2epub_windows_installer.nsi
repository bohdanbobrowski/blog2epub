; The name of the installer
!define VERSION "1.5.0"

Name "blog2epub"

; To change from default installer icon:
Icon "assets\blog2epub.ico"

; The setup filename
OutFile "dist\blog2epub_${VERSION}_setup.exe"

; The default installation directory
InstallDir $PROGRAMFILES\blog2epub

; Registry key to check for directory (so if you install again, it will
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\blog2epub" "Install_Dir"

RequestExecutionLevel admin

;--------------------------------

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "blog2epub v${VERSION} (required)"

  SectionIn RO

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR

  ; Put file there (you can add more File lines too)
  File "dist\blog2epub_gui.exe"
  ; Wildcards are allowed:
  ; File *.dll
  ; To add a folder named MYFOLDER and all files in it recursively, use this EXACT syntax:
  ; File /r MYFOLDER\*.*
  ; See: https://nsis.sourceforge.io/Reference/File
  ; MAKE SURE YOU PUT ALL THE FILES HERE IN THE UNINSTALLER TOO

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\blog2epub "Install_Dir" "$INSTDIR"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\blog2epub" "DisplayName" "blog2epub"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\blog2epub" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\blog2epub" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\blog2epub" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"
  ; SectionIn RO

  CreateDirectory "$SMPROGRAMS\blog2epub"
  CreateShortcut "$SMPROGRAMS\blog2epub\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortcut "$SMPROGRAMS\blog2epub\blog2epub.lnk" "$INSTDIR\blog2epub_gui.exe" "" "$INSTDIR\blog2epub_gui.exe" 0

SectionEnd

Section "Desktop Shortcut" SectionX
    SetShellVarContext current
    CreateShortCut "$DESKTOP\blog2epub.lnk" "$INSTDIR\blog2epub_gui.exe"
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\blog2epub"
  DeleteRegKey HKLM SOFTWARE\blog2epub

  ; Remove files and uninstaller
  ; MAKE SURE NOT TO USE A WILDCARD. IF A
  ; USER CHOOSES A STUPID INSTALL DIRECTORY,
  ; YOU'LL WIPE OUT OTHER FILES TOO
  Delete $INSTDIR\blog2epub_gui.exe
  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\blog2epub\*.*"

  ; Remove directories used (only deletes empty dirs)
  RMDir "$SMPROGRAMS\blog2epub"
  RMDir "$INSTDIR"

SectionEnd
