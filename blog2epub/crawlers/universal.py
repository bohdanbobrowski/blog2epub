from blog2epub.crawlers.abstract import AbstractCrawler


class UniversalCrawler(AbstractCrawler):
    """Attempt to create universal crawler, that can scrap website content similar like Firefox does prepare read-view
    basing on sitemap.xml file. """

    def crawl(self):
        pass

    def generate_ebook(self, **kwargs):
        pass
