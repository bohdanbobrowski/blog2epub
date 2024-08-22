from abc import ABC, abstractmethod
from typing import List, Optional

from blog2epub.models.book import ArticleModel


class AbstractCrawler(ABC):
    ignore_downloads: List[str] = []

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
