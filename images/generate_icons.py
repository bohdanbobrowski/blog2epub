import os
import sys
import pathlib
import subprocess

original_picture = "blog2epub.png"

fname = pathlib.Path(original_picture).stem
ext = pathlib.Path(original_picture).suffix
destDir = pathlib.Path(original_picture).parent

iconsetDir = os.path.join(destDir, f"{fname}.iconset")
if not (os.path.exists(iconsetDir)):
    pathlib.Path(iconsetDir).mkdir(parents=False, exist_ok=True)


class IconParameters:
    width = 0
    scale = 1

    def __init__(self, width, scale):
        self.width = width
        self.scale = scale

    def getIconName(self):
        if self.scale != 1:
            return f"icon_{self.width}x{self.width}{ext}"
        else:
            return f"icon_{self.width//2}x{self.width//2}@2x{ext}"


# https://developer.apple.com/design/human-interface-guidelines/macos/icons-and-images/app-icon#app-icon-sizes
ListOfIconParameters = [
    IconParameters(16, 1),
    IconParameters(16, 2),
    IconParameters(32, 1),
    IconParameters(32, 2),
    IconParameters(64, 1),
    IconParameters(64, 2),
    IconParameters(128, 1),
    IconParameters(128, 2),
    IconParameters(256, 1),
    IconParameters(256, 2),
    IconParameters(512, 1),
    IconParameters(512, 2),
    IconParameters(1024, 1),
    IconParameters(1024, 2),
]

# generate iconset
for ip in ListOfIconParameters:
    subprocess.call(
        [
            "sips",
            "-z",
            str(ip.width),
            str(ip.width),
            original_picture,
            "--out",
            os.path.join(iconsetDir, ip.getIconName()),
        ]
    )
    # print(f"Generated {ip.getIconName()}")

# convert iconset to icns file
subprocess.call(
    ["iconutil", "-c", "icns", iconsetDir, "-o", os.path.join(destDir, f"{fname}.icns")]
)
