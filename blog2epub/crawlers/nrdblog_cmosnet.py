from blog2epub.crawlers import DefaultCrawler
from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import BookModel


class NrdblogCmosEuArticleFactory(DefaultArticleFactory):
    pass


class NrdblogCmosEuCrawler(DefaultCrawler):
    """TODO: https://nrdblog.cmosnet.eu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "nrdblog.cmosnet.eu crawler"
        self.article_factory_class = NrdblogCmosEuArticleFactory

    def crawl(self):
        super().crawl()

    def get_book_data(self) -> BookModel:
        return super().get_book_data()
