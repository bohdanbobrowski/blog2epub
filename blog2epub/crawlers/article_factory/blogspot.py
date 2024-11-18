from typing import Optional

from lxml.html.soupparser import fromstring

from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import ArticleModel


class BlogspotArticleFactory(DefaultArticleFactory):
    def get_title(self) -> Optional[str]:
        title = super().get_title()
        if self.blog_title is not None and title == self.blog_title:
            title = "Pomidor"
        return title

    def process(self) -> ArticleModel:
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
