from typing import Dict

from blog2epub.common.exceptions import NoCrawlerDetectedError
from blog2epub.common.globals import VERSION
from blog2epub.crawlers import BlogspotCrawler, WordpressCrawler


class Blog2Epub:
    """Main Blog2Epub class."""

    version = VERSION

    def __init__(self, params: Dict):
        self.crawler = self.select_crawler(params)
        if self.crawler is None:
            raise NoCrawlerDetectedError("No crawler detected")

    @staticmethod
    def select_crawler(params: Dict):
        if params["url"].find(".blogspot.") > -1:
            return BlogspotCrawler(**params)
        return WordpressCrawler(**params)

    def download(self):
        self.crawler.crawl()
