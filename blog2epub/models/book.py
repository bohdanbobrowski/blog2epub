import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BookSynopsisModel:
    title: str | None
    subtitle: str | None
    urls: list[str]


@dataclass
class CommentModel:
    title: str | None
    date: datetime | None
    author: str | None
    content: str | None


@dataclass
class ImageModel:
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


@dataclass
class ArticleModel:
    url: str
    title: str | None
    date: datetime | None
    content: str | None
    comments: str | None  # TODO: replace with List[CommentModel]
    accessed: datetime = datetime.now()
    tags: list[str] = field(default_factory=list)
    images: list[ImageModel] = field(default_factory=list)


@dataclass
class DirModel:
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


@dataclass
class BookModel:
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
