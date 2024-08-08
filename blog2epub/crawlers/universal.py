from blog2epub.crawlers import AbstractCrawler


class UniversalCrawler(AbstractCrawler):
    """Attempt to create universal crawler, that can scrap website content similar like Firefox does prepare read-view
    basing on sitemap.xml file."""

    def _get_robots_txt(self):
        pass

    def _get_sitemap_xml(self):
        pass

    def crawl(self):
        pass

    def generate_ebook(self, **kwargs):
        pass
