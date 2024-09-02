from pathlib import Path

from pydantic import BaseModel


class ConfigurationModel(BaseModel):
    language: str = "en_US.UTF-8"
    destination_folder: str = str(Path.home())
    include_images: bool = True
    images_size: tuple[int, int] = (600, 800)
    images_quality: int = 40
