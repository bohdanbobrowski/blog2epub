from abc import ABC, abstractmethod
from typing import Optional

from lxml.html.soupparser import fromstring

from blog2epub.common.downloader import Downloader
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import ArticleModel, DirModel
from blog2epub.models.content_patterns import ContentPatterns


class AbstractArticleFactory(ABC):
    def __init__(
        self,
        url: str,
        html_content: str,
        patterns: Optional[ContentPatterns],
        interface: EmptyInterface,
        dirs: DirModel,
        language: str,
        downloader: Downloader,
    ):
        self.url = url
        self.html = html_content
        self.interface = interface
        self.dirs: DirModel = dirs
        self.language: Optional[str] = language
        self.downloader: Downloader = downloader
        self.patterns = patterns
        self.content: Optional[str] = None
        self.title: Optional[str] = None
        self.tags: list[str] = []
        self.tree = fromstring("<div></div>")
        self.comments = ""  # TODO: should be a list in the future

    @abstractmethod
    def process(self) -> ArticleModel:
        pass
