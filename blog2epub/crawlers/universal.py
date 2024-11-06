from blog2epub.crawlers import AbstractCrawler


class UniversalCrawler(AbstractCrawler):
    """Attempt to create universal crawler."""

    def crawl(self):
        self.interface.print("Crawling")

    def get_book_data(self):
        pass
