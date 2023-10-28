import os.path
from typing import Dict

from blog2epub.common.exceptions import NoCrawlerDetectedError
from blog2epub.common.globals import VERSION
from blog2epub.crawlers.blogspot import CrawlerBlogspot
from blog2epub.crawlers.wordpress import CrawlerWordpress


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
            return CrawlerBlogspot(**params)
        return CrawlerWordpress(**params)

    def download(self) -> list:
        self.crawler.save()
        cover_image_path = os.path.join(
            self.crawler.book.cover.destination_folder,
            self.crawler.book.cover.file_name + ".jpg",
        )
        generated_ebook_path = os.path.join(
            self.crawler.book.destination_folder, self.crawler.book.file_name
        )
        return [cover_image_path, generated_ebook_path]
