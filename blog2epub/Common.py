import logging
import os
import platform
import sys
from pathlib import Path


def asset_path(filename: str) -> str:
    # TODO: this needs refactor
    result = None
    if platform.system() == "Windows":
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath("./assets/")
        result = os.path.join(base_path, filename)
    elif platform.system() == "Darwin":
        in_osx_app = os.path.join(
            os.path.dirname(sys.executable).replace(
                "/Contents/MacOS", "/Contents/Resources"
            ),
            filename,
        )
        in_sources = os.path.join(
            Path(__file__).parent.resolve(), "..", "assets", filename
        )
        if os.path.isfile(in_osx_app):
            result = in_osx_app
        if os.path.isfile(in_sources):
            result = in_sources
    else:
        in_sources = os.path.join(
            Path(__file__).parent.resolve(), "..", "assets", filename
        )
        if os.path.isfile(in_sources):
            result = in_sources
    logging.info(f"Loading asset: {result}")
    return result
