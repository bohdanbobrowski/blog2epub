import PyInstaller.__main__
from pathlib import Path

HERE = Path(__file__).parent.absolute()
path_to_main = str(HERE / "blog2epub_kivy.py")


def build_windows():
    PyInstaller.__main__.run(
        [
            path_to_main,
            "--onefile",
            "--windowed",
            # '--add-data "..\\assets\\blog2epub_256px.png:."',
            # '--add-data "./assets/blog2epub.png:."',
            # '--add-data "./assets/Alegreya-Regular.ttf:."',
            # '--add-data "./assets/Alegreya-Italic.ttf:."',
            # '--add-data "./assets/MartianMono-Regular.ttf:."',
        ]
    )
