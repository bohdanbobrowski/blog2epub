#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import sys

from blog2epub.crawlers.CrawlerBlogspot import CrawlerBlogspot
from urllib import parse

class Blog2EpubCli(object):
    """
    Command line interface for Blog2Epub class.
    """

    def __init__(self, **defaults):
        params = self.parseParameters()
        params = {**defaults, **params}
        crawler = CrawlerBlogspot(**params)
        crawler.crawl()

    def getUrl(self):
        if len(sys.argv) > 1:
            if parse.urlparse(sys.argv[1]):
                return sys.argv[1]
            raise Exception("Blog url is not valid.")
        raise Exception("Not enough command line parameters.")

    def parseParameters(self):
        params = {}

        try:
            params['url'] = self.getUrl()
        except Exception as e:
            print(e)
            print("usage: blogspot2epub <blog_name> [params...]")
            exit()

        params['url'] = sys.argv[1]

        if '-n' in sys.argv or '--no-images' in sys.argv:
            params['include_images'] = False
        for arg in sys.argv:
            if arg.find('-l=') == 0:
                params['limit'] = int(arg.replace('-l=', ''))
            if arg.find('--limit=') == 0:
                params['limit'] = int(arg.replace('--limit=', ''))
            if arg.find('-s=') == 0:
                params['skip'] = int(arg.replace('-s=', ''))
            if arg.find('--skip=') == 0:
                params['skip'] = int(arg.replace('--skip=', ''))
            if arg.find('-q=') == 0:
                params['images_quality'] = int(arg.replace('-q=', ''))
            if arg.find('--quality=') == 0:
                params['images_quality'] = int(arg.replace('--quality=', ''))
        return params