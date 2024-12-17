from datetime import datetime

from lxml.html.soupparser import fromstring

from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import ArticleModel


class BlogspotArticleFactory(DefaultArticleFactory):
    def get_title(self) -> str | None:
        title = super().get_title()
        date = self.get_date()
        if isinstance(date, datetime) and (title is None or title == self.blog_title):
            title = date.strftime("%A, %d %B %Y, %H:%M")
        return title

    def process(self) -> ArticleModel | None:
        try:
            self.tree = fromstring(self.html)
            return ArticleModel(
                url=self.url,
                title=self.get_title(),
                date=self.get_date(),
                images=self.get_images(),
                tags=self.get_tags(),
                content=self.get_content(),
                comments=self.get_comments(),
            )
        except ValueError:
            self.interface.print(f"Contents of: {self.url} can not be parsed. Skipping!")
            return None
