import html
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from xml import etree
import re

from lxml.html.soupparser import fromstring

from blog2epub.common.downloader import Downloader
import dateutil

from blog2epub.common.book import Book
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import ArticleModel, DirModel
from blog2epub.models.configuration import ConfigurationModel
from blog2epub.common.crawler import (
    prepare_file_name,
    prepare_port,
    prepare_url_to_crawl,
)


class AbstractCrawler(ABC):
    def __init__(
        self,
        url: str,
        configuration: ConfigurationModel,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        file_name: Optional[str] = None,
        cache_folder: str = os.path.join(str(Path.home()), ".blog2epub"),
        interface: EmptyInterface = EmptyInterface(),
    ):
        super().__init__()
        self.url = url
        self.configuration = configuration
        self.url_to_crawl = prepare_url_to_crawl(self.url)
        self.port = prepare_port(self.url_to_crawl)
        self.file_name = prepare_file_name(file_name, self.url)
        self.cache_folder = cache_folder
        self.start = start
        self.end = end
        self.interface = interface
        self.dirs = DirModel(
            path=str(os.path.join(self.cache_folder, self.url.replace("/", "_"))),
        )
        self.book: Optional[Book]
        self.title = None
        self.subtitle = None
        self.description = None
        self.language: str | None = self.configuration.language
        self.atom_feed = False
        self.articles: List[Article] = []
        self.article_counter = 0
        self.images: List[str] = []
        self.tags: Dict = {}
        self.active = False
        self.cancelled = False
        self.ignore_downloads: List[str] = []
        self.article_class = "Article"
        self.content_xpath = (
            "//div[contains(concat(' ',normalize-space(@class),' '),'post-body')]"
        )
        self.images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
        self.articles_regex = r"<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>"
        self.downloader = Downloader(
            dirs=self.dirs,
            url=self.url,
            url_to_crawl=self.url_to_crawl,
            interface=self.interface,
            images_size=self.configuration.images_size,
            images_quality=self.configuration.images_quality,
            ignore_downloads=self.ignore_downloads,
        )

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def generate_ebook(
        self,
        articles: List[ArticleModel],
        destination_folder: str = ".",
        file_name: Optional[str] = None,
    ):  # TODO: this should be removed I guess crawler's job is just to prepare data
        pass


class Article:
    """
    Blog post, article which became book chapter...
    """

    def __init__(self, url, title, crawler):
        self.url = url
        self.title = title
        self.tags: List[str] = []
        self.interface = crawler.interface
        self.dirs: DirModel = crawler.dirs
        self.comments = ""  # TODO: should be a list in the future
        self.content_xpath = crawler.content_xpath
        self.images_regex = crawler.images_regex
        self.language: str = crawler.language
        self.images: List[str] = []
        self.images_captions = []
        self.html = None
        self.content = None
        self.date = None
        self.tree = None
        self.downloader = Downloader(crawler)

    def get_title(self):
        self.title = html.unescape(self.title.strip())

    def get_date(self):
        if isinstance(self.date, datetime):
            return
        date = self.tree.xpath('//abbr[@itemprop="datePublished"]/@title')
        if date:
            self.date = date[0]
        else:
            date = self.tree.xpath('//h2[@class="date-header"]/span/text()')
            if len(date) > 0:
                self.date = re.sub("(.*?, )", "", date[0])
        if self.date is None:
            d = self.url.split("/")
            if len(d) > 4:
                self.date = f"{d[3]}-{d[4]}-01 00:00"
            else:
                self.date = str(datetime.now())
        else:
            self.date = self._translate_month(self.date)
        try:
            self.date = dateutil.parser.parse(self.date)
        except IndexError:
            self.interface.print(f"Date not parsed: {self.date}")

    def _translate_month(self, date: str) -> str:
        date = date.lower()
        if self.language == "pl":
            replace_dict = {
                "stycznia": "january",
                "lutego": "february",
                "marca": "march",
                "kwietnia": "april",
                "maja": "may",
                "czerwca": "june",
                "lipca": "july",
                "sierpnia": "august",
                "września": "september",
                "października": "october",
                "listopada": "november",
                "grudnia": "december",
            }
            replace_dict_short = {}
            for key, val in replace_dict.items():
                date = date.replace(key, val)
                replace_dict_short[f" {key[0:3]} "] = f" {val} "
            for key, val in replace_dict_short.items():
                date = date.replace(key, val)
        if self.language == "ru":
            replace_dict = {
                "января": "january",
                "февраля": "february",
                "марта": "march",
                "апреля": "april",
                "мая": "may",
                "июня": "june",
                "июля": "july",
                "августа": "august",
                "сентября": "september",
                "октября": "october",
                "ноября": "november",
                "декабря": "december",
            }
            for key, val in replace_dict.items():
                date = date.replace(key, val)
            date = re.sub(r"\sг.$", "", date)
        logging.debug(f"Date: {date}")
        return date

    def _find_images(self):
        return re.findall(self.images_regex, self.html)

    @staticmethod
    def _default_ripper(img, img_hash, art_html):
        im_regex = (
            r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="'
            + img.replace("+", r"\+")
            + r'"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">[^<]*</td></tr>[\s]*</tbody></table>'
        )
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    @staticmethod
    def _nocaption_ripper(img: str, img_hash: str, art_html: str) -> str:
        im_regex = (
            '<a href="' + img.replace("+", r"\+") + '" imageanchor="1"[^<]*<img.*?></a>'
        )
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    @staticmethod
    def _bloggerphoto_ripper(img: str, img_hash: str, art_html: str) -> str:
        im_regex = (
            '<a href="[^"]+"><img.*?id="BLOGGER_PHOTO_ID_[0-9]+".*?src="'
            + img.replace("+", r"\+")
            + '".*?/a>'
        )
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    @staticmethod
    def _img_ripper(img, img_hash, art_html):
        im_regex = '<img.*?src="' + img.replace("+", r"\+") + '".*?>'
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    def process_images(self, images, ripper):
        for image in images:
            img = None
            caption = ""
            if isinstance(image, str):
                img = image
            elif isinstance(image, list):
                img = image[0]
                if image[1]:
                    caption = image[1]
            if img:
                img_hash = self.downloader.download_image(img)
                if img_hash:
                    self.html = ripper(img=img, img_hash=img_hash, art_html=self.html)
                    self.images.append(img_hash)
                    self.images_captions.append(caption)
        self.get_tree()

    def get_images(self):
        self.process_images(self._find_images(), self._default_ripper)
        self.process_images(
            self.tree.xpath('//a[@imageanchor="1"]/@href'), self._nocaption_ripper
        )
        self.process_images(
            self.tree.xpath('//img[contains(@id,"BLOGGER_PHOTO_ID_")]/@src'),
            self._bloggerphoto_ripper,
        )
        self.process_images(self.tree.xpath("//img/@src"), self._img_ripper)
        self.replace_images()
        self.get_tree()

    def set_content(self, content):
        self.content = content
        self.html = content
        self.get_tree()

    def replace_images(self):
        for key, image in enumerate(self.images):
            image_caption = self.images_captions[key]
            image_html = (
                '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/'
                + image
                + '" /></td></tr><tr><td class="tr-caption" style="text-align: center;">'
                + image_caption
                + "</td></tr></tbody></table>"
            )
            self.html = self.html.replace("#blog2epubimage#" + image + "#", image_html)

    def get_content(self):
        self.content = self.tree.xpath(self.content_xpath)
        if len(self.content) == 1:
            self.content = self.content[0]
            self.content = etree.tostring(self.content)
            self.content = re.sub('style="[^"]*"', "", self.content.decode("utf-8"))
            self.content = re.sub('class="[^"]*"', "", self.content)
            for src in re.findall('<iframe.+? src="([^?= ]*)', self.content):
                self.content = re.sub(
                    f"<iframe.+?{src}.+?/>",
                    f'<a href="{src}">{src}</a>',
                    self.content,
                )

    def get_tree(self):
        self.tree = fromstring(self.html)

    def get_tags(self):
        tags = self.tree.xpath('//a[@rel="tag"]//text()')
        output = []
        for t in tags:
            t = t.strip()
            output.append(t)
        self.tags = output

    def get_comments(self):
        headers = self.tree.xpath('//div[@id="comments"]/h4/text()')
        self.comments = ""
        if len(headers) == 1:
            self.comments = "<hr/><h3>" + headers[0] + "</h3>"
        comments_in_article = self.tree.xpath('//div[@class="comment-block"]//text()')
        if comments_in_article:
            tag = "h4"
            for c in comments_in_article:
                c = c.strip()
                if c not in ("Odpowiedz", "Usuń"):
                    self.comments = (
                        self.comments + "<" + tag + ">" + c + "</" + tag + ">"
                    )
                    if tag == "h4":
                        tag = "p"
                if c == "Usuń":
                    tag = "h4"
        else:
            authors = self.tree.xpath(
                '//dl[@id="comments-block"]//*[@class="comment-author"]'
            )
            comments = self.tree.xpath(
                '//dl[@id="comments-block"]//*[@class="comment-body"]'
            )
            try:
                for x in range(0, len(authors) + 1):
                    a = (
                        "".join(authors[x].xpath(".//text()"))
                        .strip()
                        .replace("\n", " ")
                    )
                    c = "".join(comments[x].xpath(".//text()")).strip()
                    self.comments += f"<h4>{a}</h4>"
                    self.comments += f"<p>{c}</p>"
            except IndexError:
                pass

    def process(self):
        self.html = self.downloader.get_content(self.url)
        if self.html is not None:
            self.get_tree()
            self.get_title()
            self.get_date()
            self.get_images()
            self.get_content()
            self.get_tags()
            self.get_comments()
