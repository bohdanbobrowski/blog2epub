#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from blog2epub.crawlers.Crawler import Crawler, Article
import atoma
import html

class CrawlerWordpressCom(Crawler):
    """
    Wordpress.com crawler.
    """

    content_xpath = "//div[contains(concat(' ',normalize-space(@class),' '),'type-post')]"
    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
    articles_regex = r'<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>'

    def __init__(self, **kwargs):
        super(CrawlerWordpressCom, self).__init__(**kwargs)

    def _get_atom_content(self):
        """ Try to load atom
        """
        atom_content = self.downloader.get_content('https://' + self.url + '/feed/atom/')
        try:
            self.atom_feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))
            return True
        except Exception as e:
            self.interface.print(e)
        return False

    def _atom_feed_loop(self):
        self.url_to_crawl = None
        for item in self.atom_feed.entries:
            try:
                self.article_counter += 1
                art = Article(item.links[0].href, html.unescape(item.title.value), self)
                self.interface.print(str(len(self.articles) + 1) + '. ' + art.title)
                art.date = item.updated
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                if item.content:
                    art.set_content(item.content.value)
                    art.get_images()
                else:
                    art.html = self.downloader.get_content(art.url)
                    art.get_tree()
                    art.get_images()
                    art._get_tags()
                    art._get_content()
                    art._get_comments()
                self.images = self.images + art.images
                self.articles.append(art)
                self._add_tags(art.tags)
                if self.limit and len(self.articles) >= self.limit:
                    break
            except Exception as e:
                self.interface.print("[article not recognized - skipping]")
