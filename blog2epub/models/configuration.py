import random
from dataclasses import field
from pathlib import Path

from pydantic import BaseModel, field_serializer

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


class ConfigurationModel(BaseModel):
    language: str = "en_US.UTF-8"
    use_cache: bool = False
    destination_folder: str = str(Path.home())
    include_images: bool = True
    images_size: tuple[int, int] = (600, 800)
    images_quality: int = 40
    images_bw: bool = True
    url: str = ""
    limit: str = "5"
    skip: str = ""
    history: list[str] = field(default_factory=list)
    email: str = ""
    version: str = ""

    @field_serializer("images_size")
    def serialize_images_size(self, images_size: tuple[int, int], _info):
        return [images_size[0], images_size[1]]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        if self.url == "":
            self.url = random.choice(example_blogs)
