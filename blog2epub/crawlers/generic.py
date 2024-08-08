from blog2epub.crawlers import AbstractCrawler


class GenericCrawler(AbstractCrawler):
    def crawl(self):
        pass

    def generate_ebook(self, **kwargs):
        pass
