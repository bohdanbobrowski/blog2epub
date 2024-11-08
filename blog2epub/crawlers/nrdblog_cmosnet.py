from blog2epub.crawlers import AbstractCrawler


class NrdblogCmosEuCrawler(AbstractCrawler):
    """TODO: https://nrdblog.cmosnet.eu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "nrdblog.cmosnet.eu crawler"

    def crawl(self):
        pass

    def get_book_data(self):
        pass
