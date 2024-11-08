from blog2epub.crawlers import AbstractCrawler


class ZeissIkonVEBCrawler(AbstractCrawler):
    """TODO: https://zeissikonveb.de"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "zeissikonveb.de crawler"

    def crawl(self):
        pass

    def get_book_data(self):
        pass
