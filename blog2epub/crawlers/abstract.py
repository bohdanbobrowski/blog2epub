import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional

from blog2epub.common.book import Book
from blog2epub.common.crawler import (
    prepare_file_name,
    prepare_port_and_url,
)
from blog2epub.common.downloader import Downloader
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.crawlers.article_factory.abstract import AbstractArticleFactory
from blog2epub.models.book import ArticleModel, BookModel, DirModel
from blog2epub.models.configuration import ConfigurationModel
from blog2epub.models.content_patterns import ContentPatterns


class AbstractCrawler(ABC):
    def __init__(
        self,
        url: str,
        configuration: ConfigurationModel,
        interface: EmptyInterface,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        file_name: Optional[str] = None,
        cache_folder: str = "",
    ):
        super().__init__()
        self.name = "abstract crawler"
        self.port, self.url = prepare_port_and_url(url)
        self.configuration = configuration
        self.file_name = prepare_file_name(file_name, self.url)
        self.cache_folder = cache_folder
        self.start = start
        self.end = end
        self.interface = interface
        self.dirs = DirModel(
            path=str(
                os.path.join(
                    self.cache_folder,
                    self.url.replace("http://", "").replace("https://", "").replace("/", "_"),
                )
            ),
        )
        self.book: Optional[Book]
        self.title = None
        self.subtitle = None
        self.description = None
        self.language: str | None = self.configuration.language
        self.atom_feed = False
        self.articles: list[ArticleModel] = []
        self.article_counter = 0
        self.images: list[str] = []
        self.tags: Dict = {}
        self.active = False
        self.cancelled = False
        self.ignore_downloads: list[str] = [
            r"[http|https]+:\/\/zblogowani.pl[^\s]+",
        ]
        self.article_factory_class = AbstractArticleFactory
        self.patterns: Optional[ContentPatterns] = None
        self.downloader = Downloader(
            dirs=self.dirs,
            url=self.url,
            interface=self.interface,
            images_size=self.configuration.images_size,
            images_quality=self.configuration.images_quality,
            ignore_downloads=self.ignore_downloads,
        )

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def get_book_data(self) -> BookModel:
        pass
