#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from blog2epub.crawlers.Crawler import Crawler, Article
import atoma
import html
from lxml.html.soupparser import fromstring
from lxml.ElementInclude import etree
import re


class CrawlerWordpress(Crawler):
    """Wordpress.com crawler."""

    article_class = "ArticleWordpressCom"

    content_xpath = (
        "//div[contains(concat(' ',normalize-space(@class),' '),'type-post')]"
    )
    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
    articles_regex = r"<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>"


    def __init__(self, **kwargs):
        super(CrawlerWordpress, self).__init__(**kwargs)

    def _get_atom_content(self, page=1):
        url = "https://" + self.url + "/feed/atom/"
        if page > 1:
            url = url + f"?paged={page}"
            self.interface.print(f"[downloading next page: {url}]")
        atom_content = self.downloader.get_content(url)
        self.atom_feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))
        return True
        self.interface.print(e)
        return False

    def _atom_feed_loop(self):
        self.url_to_crawl = None
        next_page = 2
        while next_page:
            for item in self.atom_feed.entries:
                self.article_counter += 1
                art = eval(self.article_class)(
                    item.links[0].href, html.unescape(item.title.value), self
                )
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
                    art.process()
                for category in item.categories:
                    art.tags.append(category.term)
                self.images = self.images + art.images
                self.articles.append(art)
                self._add_tags(art.tags)
                if self.limit and len(self.articles) >= self.limit:
                    next_page = None
                    break
            if next_page:
                self._get_atom_content(next_page)
                if not self.atom_feed or not self.atom_feed.entries:
                    break
                next_page = next_page + 1


class ArticleWordpressCom(Article):

    images_xpaths = [
        '//img[contains(@class, "size-full")]',
        '//figure[contains(@class, "wp-block-image")]//img',
        '//div[contains(@class, "wp-block-image")]//img',
        '//img'
    ]

    def get_images(self):
        self.get_images_with_captions()
        for x in self.images_xpaths:
            self.interface.print(f" *** XPATH {x}")
            self.get_single_images(self.tree.xpath(x))
        self.replace_images()
        self.get_tree()

    def get_single_images(self, images) -> None:
        for img in images:
            img_url = img.attrib.get("data-orig-file")
            if not img_url:
                img_url = img.attrib.get("src")
            if img_url:
                img_url = img_url.split("?")[0]
                self.interface.print(img_url)
                img_caption = img.attrib.get("data-image-title")
                if not img_caption:
                    img_caption = img.attrib.get("title")
                if not img_caption:
                    img_caption = img.attrib.get("alt")
                img_hash = self.downloader.download_image(img_url)

                if img_hash:
                    img_parent = img.getparent()
                    if img_parent:
                        if img_hash:
                            blog2epub_img = f"#blog2epubimage#{img_hash}#"
                            img_parent.text = blog2epub_img
                        else:
                            img_parent.text = ""
                        self.tree = img_parent.getroottree()
                    self.html = etree.tostring(self.tree).decode("utf-8")
                    self.images.append(img_hash)
                    self.images_captions.append(img_caption)

    def get_images_with_captions(self):
        images_c = self.tree.xpath('//div[contains(@class, "wp-caption")]')
        for img in images_c:
            img_html = etree.tostring(img).decode("utf-8")
            img_tr = fromstring(img_html)
            img_url = img_tr.xpath("//img/@src")[0]
            img_caption = img_tr.xpath('//p[@class="wp-caption-text"]/text()').pop()
            img_hash = self.downloader.download_image(img_url)
            img_parent = img.getparent()
            img_parent.replace(img, etree.Comment(f"#blog2epubimage#{img_hash}"))
            self.tree = img_parent.getroottree()
            self.html = etree.tostring(self.tree).decode("utf-8")
            self.images.append(img_hash)
            self.images_captions.append(img_caption)

    def replace_images(self):
        for key, image in enumerate(self.images):
            if image:
                image_caption = ""
                if self.images_captions[key]:
                    image_caption = self.images_captions[key]
                image_html = (
                    '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/'
                    + image
                    + '" /></td></tr><tr><td class="tr-caption" style="text-align: center;">'
                    + image_caption
                    + "</td></tr></tbody></table>"
                )
                self.html = self.html.replace(
                    "<!--#blog2epubimage#" + image + "#-->", image_html
                )

    def get_content(self):
        article_header = re.findall(
            r"(<h1 class=\"entry-title\">[^<]*<\/h1>)", self.html
        )
        if article_header:
            self.html = self.html.split(article_header[0])[1]
        article_footer = re.findall(r"(<div id=\"atatags-[^\"]*\")", self.html)
        if article_footer:
            self.html = self.html.split(article_footer[0])[0]
        self.content = self.html = self.html.strip()
        self.get_tree()

    def get_tags(self):
        pass
