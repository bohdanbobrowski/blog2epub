import random
from dataclasses import dataclass
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

example_blogs = [
    "http://archaia-ellada.blogspot.com",
    "http://historicaltidbits.blogspot.com",
    "http://starybezpiek.blogspot.com",
    "https://19thcentury.wordpress.com",
    "https://cyclehistory.wordpress.com",
    "https://klubjagiellonski.pl",
    "https://knippsen.blogspot.com",
    "https://ksgedania.blogspot.com",
    "https://motorbikes.blog",
    "https://nrdblog.cmosnet.eu",
    "https://oldcam.wordpress.com",
    "https://oldcamera.blog",
    "https://python-bloggers.com",
    "https://rocket-garage.blogspot.com",
    "https://swiatmotocykli.pl",
    "https://thevictoriancyclist.wordpress.com",
    "https://velosov.blogspot.com",
    "https://vintagebicycle.wordpress.com",
    "https://vowe.net",
    "https://www.blog.homebrewing.pl",
    "https://www.historyoftheancientworld.com",
    "https://www.infolotnicze.pl",
    "https://www.mikeanderson.biz",
    "https://www.nomadicmatt.com",
    "https://www.returnofthecaferacers.com",
    "https://www.szarmant.pl",
]


@dataclass
class ConfigurationModel:
    history: list[str]
    language: str = "en_US.UTF-8"
    use_cache: bool = False
    destination_folder: str = str(Path.home())
    include_images: bool = INCLUDE_IMAGES["Yes"]
    images_size: tuple[int, int] = IMAGE_SIZES[0]
    images_quality: int = 40
    images_bw: bool = IMAGE_COL_MODES["BW"]
    url: str = ""
    limit: str = "5"
    skip: str = ""
    email: str = ""
    version: str = ""

    def __init__(self, **kwargs) -> None:
        self.history = []
        if self.url == "":
            self.url = random.choice(example_blogs)
