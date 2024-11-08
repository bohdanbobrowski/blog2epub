#!/usr/bin/env python3
# -*- coding : utf-8 -*-

import html

import atoma  # type: ignore

from blog2epub.crawlers.article_factory.wordpress import WordpressArticleFactory
from blog2epub.crawlers.default import DefaultCrawler


class WordpressCrawler(DefaultCrawler):
    """Wordpress.com crawler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "wordpress crawler"
        self.article_factory_class = WordpressArticleFactory
        self.content_xpath = "//div[contains(concat(' ',normalize-space(@class),' '),'type-post')]"
        self.images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
        self.articles_regex = (
            r"<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>"
        )

    def _get_atom_content(self, page=1):
        url = "https://" + self.url + "/feed/atom/"
        if page > 1:
            url = url + f"?paged={page}"
            self.interface.print(f"[downloading next page: {url}]")
        atom_content = self.downloader.get_content(url)
        self.atom_feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))

    def _atom_feed_loop(self):
        # TODO: This needs refactor!
        next_page = 2
        while next_page:
            for item in self.atom_feed.entries:
                self.article_counter += 1
                art = self.article_factory_class(item.links[0].href, html.unescape(item.title.value), self)
                self.interface.print(str(len(self.articles) + 1) + ". " + art.title)
                art.date = item.published
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                if item.content:
                    art.set_content(item.content.value)
                    art.get_images()
                else:
                    art.html = self.downloader.get_content(art.url)
                    # art.process()
                # for category in item.categories:
                #     art.tags.append(category.term)
                self.articles.append(art.process())
                # self._add_tags(art.tags)
                if self.configuration.limit and len(self.articles) >= int(self.configuration.limit):
                    next_page = None
                    break
            if next_page:
                self._get_atom_content(next_page)
                if not self.atom_feed or not self.atom_feed.entries:
                    break
                next_page = next_page + 1
