#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from blog2epub.crawlers.CrawlerBlogspot import CrawlerBlogspot

class Blog2Epub(object):
    """
    Main Blog2Epub class.
    """

    def __init__(self, params):
        self.crawler = self._selectCrawler(params)

    def _selectCrawler(self, params):
        return CrawlerBlogspot(**params)

    def download(self):
        self.crawler.save()

