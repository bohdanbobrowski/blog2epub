import hashlib
import os
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookSynopsisModel(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    urls: list[str]


class CommentModel(BaseModel):
    title: Optional[str]
    date: Optional[datetime]
    author: Optional[str]
    content: Optional[str]


class ImageModel(BaseModel):
    url: str
    description: Optional[str]

    @property
    def hash(self) -> str:
        m = hashlib.md5()
        m.update(self.url.encode("utf-8"))
        return m.hexdigest()

    @property
    def file_name(self):
        return f"{self.hash}.jpg"


class ArticleModel(BaseModel):
    url: str
    title: Optional[str]
    date: Optional[datetime]
    content: Optional[str]
    comments: Optional[str]  # TODO: replace with List[CommentModel]
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
    title: Optional[str]
    subtitle: Optional[str]
    description: Optional[str]
    dirs: DirModel
    articles: list[ArticleModel]
    images: list[ImageModel]
    start: Optional[datetime]
    end: Optional[datetime]
    file_name_prefix: Optional[str]
    destination_folder: Optional[str]
    cover: Optional[str]
    cover_image_path: Optional[str]
