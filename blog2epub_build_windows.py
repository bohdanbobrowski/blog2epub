from pathlib import Path

import PyInstaller.__main__

HERE = Path(__file__).parent.absolute()
blog2epub_windows_spec = str(HERE / "blog2epub_windows.spec")
PyInstaller.__main__.run([blog2epub_windows_spec])
