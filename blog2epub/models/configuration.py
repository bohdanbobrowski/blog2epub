from dataclasses import dataclass, field
from pathlib import Path

INCLUDE_IMAGES = {
    "Yes": True,
    "No": False,
}

IMAGE_SIZES = [
    (600, 800),
    (640, 960),
    (1236, 1648),
]

IMAGE_COL_MODES = {
    "BW": True,
    "RGB": False,
}


@dataclass
class ConfigurationModel:
    history: list[str] = field(default_factory=list)
    language: str = "en_US.UTF-8"
    use_cache: bool = False
    destination_folder: str = str(Path.home())
    include_images: bool = INCLUDE_IMAGES["Yes"]
    images_size: tuple[int, int] = IMAGE_SIZES[0]
    images_quality: int = 40
    images_bw: bool = IMAGE_COL_MODES["BW"]
    url: str = ""
    limit: str = ""
    skip: str = ""
    email: str = ""
    version: str = ""
