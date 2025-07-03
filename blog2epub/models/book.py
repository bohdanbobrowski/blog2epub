import hashlib
import os
from datetime import datetime

from pydantic import BaseModel


class BookSynopsisModel(BaseModel):
    title: str | None
    subtitle: str | None
    urls: list[str]


class CommentModel(BaseModel):
    title: str | None
    date: datetime | None
    author: str | None
    content: str | None


class ImageModel(BaseModel):
    url: str
    description: str = ""
    file_path: str = ""
    resized_fn: str = ""
    resized_path: str = ""

    @property
    def hash(self) -> str:
        m = hashlib.md5()
        m.update(self.url.encode("utf-8"))
        return m.hexdigest()

    def __hash__(self):
        return hash(self.hash)

    @property
    def file_name(self) -> str:
        return f"{self.hash}.jpg"

    @property
    def type(self) -> str:
        img_type = os.path.splitext(self.url)[1].lower()
        return img_type.split("?")[0]

    @property
    def is_supported(self) -> bool:
        if self.type in [".jpeg", ".jpg", ".png", ".bmp", ".gif", ".webp", ".heic"]:
            return True
        return False


class ArticleModel(BaseModel):
    url: str
    title: str | None
    date: datetime | None
    accessed: datetime = datetime.now()
    content: str | None
    comments: str | None  # TODO: replace with List[CommentModel]
    tags: list[str] = []
    images: list[ImageModel] = []


class DirModel(BaseModel):
    path: str

    @property
    def html(self) -> str:
        return os.path.join(self.path, "html")

    @property
    def images(self) -> str:
        return os.path.join(self.path, "images")

    @property
    def originals(self) -> str:
        return os.path.join(self.path, "originals")


class BookModel(BaseModel):
    url: str
    title: str | None
    subtitle: str | None
    description: str | None
    dirs: DirModel
    articles: list[ArticleModel]
    images: list[ImageModel]
    start: datetime | None
    end: datetime | None
    file_name_prefix: str | None
    destination_folder: str | None
    cover: str | None
    cover_image_path: str | None
