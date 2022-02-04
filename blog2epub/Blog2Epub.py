#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from blog2epub.crawlers.CrawlerBlogspot import *
from blog2epub.crawlers.CrawlerWordpress import *


class Blog2Epub(object):
    """Main Blog2Epub class."""

    VERSION = "1.2.0"

    def __init__(self, params):
        self.crawler = self.select_crawler(params)
        if self.crawler is None:
            raise Exception("No crawler detected")

    @staticmethod
    def select_crawler(params):
        if params["url"].find(".blogspot.") > -1:
            return CrawlerBlogspot(**params)
        return CrawlerWordpress(**params)

    def download(self):
        self.crawler.save()
