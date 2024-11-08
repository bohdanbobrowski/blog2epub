from pathlib import Path

import PyInstaller.__main__

HERE = Path(__file__).parent.absolute()
blog2epub_gui_windows_spec = str(HERE / "blog2epub_gui_windows.spec")
blog2epub_gui_macos_spec = str(HERE / "blog2epub_gui_macos.spec")


def build_gui_windows():
    PyInstaller.__main__.run([blog2epub_gui_windows_spec])


def build_gui_macos():
    PyInstaller.__main__.run([blog2epub_gui_macos_spec])
