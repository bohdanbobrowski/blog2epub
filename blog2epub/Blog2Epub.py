#!/usr/bin/env python3
# -*- coding : utf-8 -*-

from blog2epub.crawlers.Crawler import Crawler
from blog2epub.crawlers.CrawlerBlogspot import CrawlerBlogspot

class Blog2Epub(object):
    """
    Main Blog2Epub class.
    """

    def __init__(self, url, params={}):
        self.url = url
        self.crawler = self._selectCrawler(url, params)

    def _selectCrawler(self, url, params):
        self.crawler = Crawler(params)
        self.crawler = CrawlerBlogspot(params)

    def download(self):
        self.crawler.crawl()
        self.crawler.save()

