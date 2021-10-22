#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from blog2epub.crawlers.Crawler import Crawler, Article
import atoma
import html
from lxml.html.soupparser import fromstring
from lxml.ElementInclude import etree
# from lxml.etree import etree
import re


class CrawlerWordpressCom(Crawler):
    """ Wordpress.com crawler.
    """

    article_class = "ArticleWordpressCom"

    content_xpath = "//div[contains(concat(' ',normalize-space(@class),' '),'type-post')]"
    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
    articles_regex = r'<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>'

    def __init__(self, **kwargs):
        super(CrawlerWordpressCom, self).__init__(**kwargs)

    def _get_atom_content(self):
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
                art = eval(self.article_class)(item.links[0].href, html.unescape(item.title.value), self)
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
                    art.process()
                self.images = self.images + art.images
                self.articles.append(art)
                self._add_tags(art.tags)
                if self.limit and len(self.articles) >= self.limit:
                    break
            except Exception as e:
                self.interface.print("[article not recognized - skipping]")


class ArticleWordpressCom(Article):

    def get_images(self):
        images_c = self.tree.xpath('//div[contains(@class, "wp-caption")]')
        for img in images_c:
            img_html = etree.tostring(img).decode("utf-8")
            img_tr = fromstring(img_html)
            img_url = img_tr.xpath('//img/@src')[0]
            img_caption = img_tr.xpath('//p[@class="wp-caption-text"]/text()').pop()
            img_hash = self.downloader.download_image(img_url)
            img_parent = img.getparent()
            img_parent.replace(img, etree.Comment("#blog2epubimage#{}#".format(img_hash)))
            self.html = etree.tostring(self.tree).decode("utf-8")
            self.images.append(img_hash)
            self.images_captions.append(img_caption)
        self.get_tree()

    def _get_content(self):
        try:
            article_header = re.findall(r"(<h1 class=\"entry-title\">[^<]*<\/h1>)", self.html)[0]
            article_footer = re.findall(r"(<div id=\"atatags-[a-z0-9\-]*\"></div>)", self.html)[0]
            self.html = self.html.split(article_header)[1]
            self.html = self.html.split(article_footer)[0]
            self.content = self.html = self.html.strip()
        except Exception as e:
            self.interface.print("{}: {}".forma(__file__, e))
