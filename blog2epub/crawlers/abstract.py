from abc import ABC, abstractmethod
from typing import List


class AbstractCrawler(ABC):
    ignore_downloads: List[str] = []

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def generate_ebook(
        self, **kwargs
    ):  # TODO: this should be removed I guess crawler's job is just to prepare data
        pass
