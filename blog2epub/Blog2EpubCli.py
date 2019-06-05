#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import sys


class Blog2EpubCli(object):
    """
    Command line interface for Blog2Epub class.
    """

    def __init__(self):
        pass

    def parseParameters(self):
        params = {}
        if len(sys.argv) < 2:
            print("usage: blogspot2epub <blog_name> [params...]")
            exit()
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

    def main(self):
        params = self.parseParameters()

        # TODO:
        crawler = CrawlerBlogspot(**params)
        crawler.crawl()
