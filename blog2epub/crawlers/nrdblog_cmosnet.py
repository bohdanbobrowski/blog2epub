import html
import re

from blog2epub.crawlers import DefaultCrawler
from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import BookModel
from blog2epub.models.content_patterns import Pattern


class NrdblogCmosEuArticleFactory(DefaultArticleFactory):
    pass


class NrdblogCmosEuCrawler(DefaultCrawler):
    """https://nrdblog.cmosnet.eu"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "nrdblog.cmosnet.eu crawler"
        self.article_factory_class = NrdblogCmosEuArticleFactory
        self.patterns.title = [
            Pattern(
                regex="<title>([^>^<]*)</title>",
            ),
        ]
        self.patterns.content_cleanup.append(
            Pattern(
                xpath='//div[@class="bawmrp"]',
            )
        )

    def _get_blog_title(self, content: str | bytes) -> str:
        title = ""
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        if re.search("<title>([^>^<]*)</title>", content):
            title = re.search("<title>([^>^<]*)</title>", content).group(1).strip()  # type: ignore
        return html.unescape(title)

    def crawl(self):
        super().crawl()

    def get_book_data(self) -> BookModel:
        return super().get_book_data()
