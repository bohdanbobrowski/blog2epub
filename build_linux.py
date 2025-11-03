from pathlib import Path

import PyInstaller.__main__

HERE = Path(__file__).parent.absolute()
blog2epub_linux_spec = str(HERE / "blog2epub_linux.spec")
PyInstaller.__main__.run([blog2epub_linux_spec])
