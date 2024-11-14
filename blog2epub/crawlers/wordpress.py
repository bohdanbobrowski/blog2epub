#!/usr/bin/env python3
# -*- coding : utf-8 -*-


from blog2epub.crawlers.article_factory.wordpress import WordpressArticleFactory
from blog2epub.crawlers.default import DefaultCrawler
from blog2epub.models.content_patterns import Pattern


class WordpressCrawler(DefaultCrawler):
    """Wordpress.com crawler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "wordpress crawler"
        self.article_factory_class = WordpressArticleFactory
        self.patterns.images = [
            Pattern(xpath='//img[contains(@class, "size-full")]'),
            Pattern(xpath='//figure[contains(@class, "wp-block-image")]//img'),
            Pattern(xpath='//div[contains(@class, "wp-block-image")]//img'),
            Pattern(xpath="//img"),
            Pattern(
                regex=r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
            ),
        ]
        # self.patterns.content = [Pattern(xpath="//div[contains(concat(' ',normalize-space(@class),' '),'type-post')]")]
