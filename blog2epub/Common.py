import os
import sys


def asset_path(filename: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath("./assets/")
    return os.path.join(base_path, filename)
