import os
import pathlib
import subprocess

ORIGINAL_PICTURE = "blog2epub.png"

f_name = pathlib.Path(ORIGINAL_PICTURE).stem
ext = pathlib.Path(ORIGINAL_PICTURE).suffix
destDir = pathlib.Path(ORIGINAL_PICTURE).parent

icons_dir = os.path.join(destDir, f"{f_name}.iconset")
if not (os.path.exists(icons_dir)):
    pathlib.Path(icons_dir).mkdir(parents=False, exist_ok=True)


class IconParameters:
    width = 0
    scale = 1

    def __init__(self, width, scale):
        self.width = width
        self.scale = scale

    def get_icon_name(self):
        if self.scale != 1:
            return f"icon_{self.width}x{self.width}{ext}"
        return f"icon_{self.width // 2}x{self.width // 2}@2x{ext}"


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
            ORIGINAL_PICTURE,
            "--out",
            os.path.join(icons_dir, ip.get_icon_name()),
        ]
    )

# convert iconset to icns file
subprocess.call(
    [
        "iconutil",
        "-c",
        "icns",
        icons_dir,
        "-o",
        os.path.join(destDir, f"{f_name}.icns"),
    ]
)
