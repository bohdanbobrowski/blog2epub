#!/usr/bin/env python3
# -*- coding : utf-8 -*-

from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.crawlers.default import DefaultCrawler
from blog2epub.models.content_patterns import Pattern


class WordpressArticleFactory(DefaultArticleFactory):
    pass


class WordpressCrawler(DefaultCrawler):
    """Wordpress.com crawler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "wordpress crawler"
        self.article_factory_class = WordpressArticleFactory
        self.patterns.content += [
            Pattern(xpath='//div[contains(@class,"type-post")]'),
            Pattern(xpath="//div[contains(concat(' ',normalize-space(@class),' '),'type-post')]"),
        ]
        self.patterns.images += [
            Pattern(xpath='//div[contains(@class,"type-post")]//img'),
            Pattern(xpath='//img[contains(@class, "size-full")]'),
            Pattern(xpath='//figure[contains(@class, "wp-block-image")]//img'),
            Pattern(xpath='//div[contains(@class, "wp-block-image")]//img'),
            Pattern(xpath="//img"),
            Pattern(
                regex=r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
            ),
        ]
        self.patterns.title += [
            Pattern(xpath="//*[contains(@class, 'entry-title')]"),
        ]
        self.patterns.content_cleanup += []
