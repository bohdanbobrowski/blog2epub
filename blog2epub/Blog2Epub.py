from typing import Dict

from blog2epub.crawlers.CrawlerBlogspot import Crawler, CrawlerBlogspot
from blog2epub.crawlers.CrawlerWordpress import CrawlerWordpress

VERSION = "1.2.4"


class NoCrawlerDetectedError(Exception):
    pass


class BadUrlException(Exception):
    pass


class NotEnoughCommandsException(Exception):
    pass


class Blog2Epub:
    """Main Blog2Epub class."""

    version = VERSION

    def __init__(self, params: Dict):
        self.crawler = self.select_crawler(params)
        if self.crawler is None:
            raise NoCrawlerDetectedError("No crawler detected")

    @staticmethod
    def select_crawler(params: Dict) -> Crawler:
        if params["url"].find(".blogspot.") > -1:
            return CrawlerBlogspot(**params)
        return CrawlerWordpress(**params)

    def download(self):
        self.crawler.save()
