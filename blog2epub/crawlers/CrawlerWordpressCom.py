#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from blog2epub.crawlers.Crawler import Crawler
import atoma

class CrawlerWordpressCom(Crawler):
    """
    Wordpress.com crawler.
    """

    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
    articles_regex = r'<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>'

    def __init__(self, **kwargs):
        super(CrawlerWordpressCom, self).__init__(**kwargs)

    def _get_atom_content(self):
        atom_content = self.downloader.get_content('https://' + self.url + '/feed')
        try:
            feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))
            self.atom_feed = feed
        except Exception as e:
            self.interface.print(e)
