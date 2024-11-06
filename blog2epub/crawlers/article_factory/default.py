# TODO: move Article class login from abstract_crawler.py here
# it should return ArticleModel objects
from blog2epub.crawlers.article_factory.abstract import AbstractArticleFactory


class DefaultArticleFactory(AbstractArticleFactory):
    def process(self):
        pass
