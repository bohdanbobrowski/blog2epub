from pathlib import Path
from typing import List

from pydantic import BaseModel


class ConfigurationModel(BaseModel):
    language: str = "en_US.UTF-8"
    destination_folder: str = str(Path.home())
    include_images: bool = True
    images_size: List[int] = [600, 800]
    images_quality: int = 40
    url: str = ""
    limit: str = ""
    skip: str = ""
    history: List[str] = []

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
