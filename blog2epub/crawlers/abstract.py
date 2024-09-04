import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from blog2epub.common.book import Book
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.crawlers.default import Article, Downloader
from blog2epub.models.book import ArticleModel, DirModel
from blog2epub.models.configuration import ConfigurationModel
from blog2epub.common.crawler import (
    prepare_file_name,
    prepare_port,
    prepare_url_to_crawl,
)


class AbstractCrawler(ABC):
    ignore_downloads: List[str] = []

    def __init__(
        self,
        url: str,
        configuration: ConfigurationModel,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        file_name: Optional[str] = None,
        cache_folder: str = os.path.join(str(Path.home()), ".blog2epub"),
        interface: EmptyInterface = EmptyInterface(),
    ):
        super().__init__()
        self.url = url
        self.configuration = configuration
        self.url_to_crawl = prepare_url_to_crawl(self.url)
        self.port = prepare_port(self.url_to_crawl)
        self.file_name = prepare_file_name(file_name, self.url)
        self.cache_folder = cache_folder
        self.start = start
        self.end = end
        self.interface = interface
        self.dirs = DirModel(
            path=str(os.path.join(self.cache_folder, self.url.replace("/", "_"))),
        )
        self.book: Optional[Book]
        self.title = None
        self.subtitle = None
        self.description = None
        self.language: str | None = self.configuration.language
        self.atom_feed = False
        self.articles: List[Article] = []
        self.article_counter = 0
        self.images: List[str] = []
        self.downloader = Downloader(self)
        self.tags: Dict = {}
        self.active = False
        self.cancelled = False

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def generate_ebook(
        self,
        articles: List[ArticleModel],
        destination_folder: str = ".",
        file_name: Optional[str] = None,
    ):  # TODO: this should be removed I guess crawler's job is just to prepare data
        pass
