from pydantic import BaseModel


class ConfigurationModel(BaseModel):
    language: str = "en_US.UTF-8"
    include_images: bool = True
    images_size: tuple[int] = (600, 800)
    images_quality: int = 40
