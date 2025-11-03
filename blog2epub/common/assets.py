import os
import sys
import sysconfig


def asset_path(filename: str) -> str:
    """TODO: this should be refactored"""
    # Elegant part:
    filepath = os.path.join(sysconfig.get_paths()["purelib"], "assets", filename)
    if os.path.isfile(filepath):
        return os.path.join(filepath)
    # Dirty part:
    try:
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath("./assets/")
    filepath = os.path.join(base_path, filename)
    if os.path.isfile(filepath):
        return os.path.join(filepath)
    # if there is no given file I'm guessing that blog2epub is run from sources
    return os.path.join(os.path.abspath("../assets/"), filename)
