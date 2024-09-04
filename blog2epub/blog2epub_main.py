from blog2epub.common.globals import VERSION
from blog2epub.crawlers import BlogspotCrawler, WordpressCrawler


class Blog2Epub:
    """Main Blog2Epub class."""

    version = VERSION

    def __init__(self, **kwargs):
        if kwargs.get("url").find(".blogspot.") > -1:
            self.crawler = BlogspotCrawler(**kwargs)
        self.crawler = WordpressCrawler(**kwargs)

    def download(self):
        self.crawler.crawl()
