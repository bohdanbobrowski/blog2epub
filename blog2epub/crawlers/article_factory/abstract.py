from abc import ABC, abstractmethod
from typing import Callable, Optional

from lxml.html.soupparser import fromstring

from blog2epub.common.downloader import Downloader
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import ArticleModel, DirModel, ImageModel
from blog2epub.models.content_patterns import ContentPatterns


class AbstractArticleFactory(ABC):
    def __init__(
        self,
        url: str,
        html_content: bytes,
        patterns: Optional[ContentPatterns],
        interface: EmptyInterface,
        dirs: DirModel,
        language: str,
        downloader: Downloader,
        cancelled: bool = False,
        download_callback: Optional[Callable] = None,
    ):
        self.url = url
        self.html: bytes = html_content
        self.interface = interface
        self.dirs: DirModel = dirs
        self.language: Optional[str] = language
        self.downloader: Downloader = downloader
        self.patterns = patterns
        self.content: Optional[str] = None
        self.title: Optional[str] = None
        self.tags: list[str] = []
        self.tree = fromstring("<div></div>")
        self.images_list: list[ImageModel] = []
        self.comments = ""  # TODO: should be a list in the future
        self.cancelled: bool = cancelled
        self.download_callback = download_callback

    @abstractmethod
    def process(self) -> ArticleModel:
        pass
