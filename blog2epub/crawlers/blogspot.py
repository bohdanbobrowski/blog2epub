#!/usr/bin/env python3
# -*- coding : utf-8 -*-

from blog2epub.crawlers.article_factory.blogspot import BlogspotArticleFactory
from blog2epub.crawlers.default import DefaultCrawler
from blog2epub.models.content_patterns import Pattern


class BlogspotCrawler(DefaultCrawler):
    """Blogspot.com crawler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "blogger.com crawler"
        self.article_factory_class = BlogspotArticleFactory
        self.patterns.content.append(
            Pattern(
                xpath="//div[contains(@class, 'post-body')]",
            )
        )
        self.patterns.images.append(
            Pattern(
                xpath="//div[contains(@class, 'post-body')]//img",
            )
        )
        self.patterns.content.append(
            Pattern(
                xpath='//div[contains(@itemprop, "articleBody")]',
            )
        )

        self.ignore_downloads += [
            r"https:\/\/www.blogger.com\/img\/blogger_logo_[a-z]+_[0-9]+\.png",
            r"https:\/\/resources.blogblog.com\/img\/[a-z0-9_]+.gif",
            r"https:\/\/resources.blogblog.com\/img\/icon_feed[0-9]+.png",
            r"https:\/\/www.paypalobjects.com\/[a-zA-Z_]+\/i\/scr\/pixel.gif",
            r"https:\/\/resources.blogblog.com\/img\/widgets\/[a-zA-Z0-9\-\.]+",
            r"https:\/\/[a-zA-Z0-9\.\/\-\_]+icon[0-9]+_[a-z]+.gif",
        ]
