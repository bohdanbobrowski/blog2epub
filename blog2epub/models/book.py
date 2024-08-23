import os
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class BookSynopsisModel(BaseModel):
    title: Optional[str]
    subtitle: Optional[str]
    urls: List[HttpUrl]


class CommentModel(BaseModel):
    title: Optional[str]
    date: Optional[datetime]
    author: Optional[str]
    content: Optional[str]


class ArticleModel(BaseModel):
    url: HttpUrl
    title: Optional[str]
    date: Optional[datetime]
    content: Optional[str]
    comments: Optional[str]  # TODO: replace with List[CommentModel]
    tags: List[str] = []


class ImageModel(BaseModel):
    hash: str
    url: Optional[str]
    description: Optional[str]


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
    articles: List[ArticleModel]
    images: List[ImageModel]
    start: Optional[datetime]
    end: Optional[datetime]
    file_name_prefix: Optional[str]
    destination_folder: Optional[str]
    cover: Optional[str]
    cover_image_path: Optional[str]
