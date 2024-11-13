from typing import Optional

from blog2epub.crawlers import DefaultCrawler
from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import BookModel
from blog2epub.models.content_patterns import Pattern


class ZeissIkonVEBArticleFactory(DefaultArticleFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.language = "de"

    def get_title(self) -> Optional[str]:
        try:
            title = super().get_title()
            if title:
                return title.split("|")[0]
        except IndexError:
            pass
        return None


class ZeissIkonVEBCrawler(DefaultCrawler):
    """TODO: https://zeissikonveb.de"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "zeissikonveb.de crawler"
        self.article_factory_class = ZeissIkonVEBArticleFactory
        self.patterns.content = [Pattern(xpath='//div[@id="Section1"]')]
        self.patterns.content_cleanup = [
            Pattern(xpath='//div[@data-kind="MENU"]'),
            Pattern(regex=r"background-color:rgba(255,255,255,1);color:rgba(156,156,156,1);"),
            Pattern(regex=r"font-size:[0-9]+px\;"),
            Pattern(regex=r"line-height:[0-9]+\;"),
            Pattern(regex=r"font-family:Arial, Helvetica, sans-serif"),
        ]
        self.patterns.date = [
            Pattern(regex=r"letzte Änderung[\s:]*([0-9]{1,2})[\.\s]*([A-Za-z]+)[\.\s]*([0-9]{4})"),
            Pattern(regex=r"letzte Aktualisierung[\s:]*([0-9]{1,2})[\.\s]*([A-Za-z]+)[\.\s]*([0-9]{4})"),
        ]
        self.patterns.images = [
            Pattern(xpath='//div[@data-kind="IMAGE"]//img'),
        ]

    def _get_blog_language(self, content) -> str:
        return "de"

    def crawl(self):
        super().crawl()

    def get_book_data(self) -> BookModel:
        return super().get_book_data()
