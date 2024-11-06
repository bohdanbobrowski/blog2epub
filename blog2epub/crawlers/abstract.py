import html
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict
import re

from lxml.html.soupparser import fromstring
from lxml.etree import tostring
from strip_tags import strip_tags  # type: ignore

from blog2epub.common.downloader import Downloader
import dateutil

from blog2epub.common.book import Book
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.common.language_tools import translate_month
from blog2epub.models.book import DirModel, BookModel
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
        cache_folder: str = "",
        interface: EmptyInterface = EmptyInterface(),
    ):
        super().__init__()
        self.url_to_crawl = self.url = prepare_url_to_crawl(url)
        self.configuration = configuration
        self.port = prepare_port(self.url_to_crawl)
        self.file_name = prepare_file_name(file_name, self.url)
        self.cache_folder = cache_folder
        self.start = start
        self.end = end
        self.interface = interface
        self.dirs = DirModel(
            path=str(
                os.path.join(
                    self.cache_folder,
                    self.url.replace("http://", "")
                    .replace("https://", "")
                    .replace("/", "_"),
                )
            ),
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
        self.article_class = Article
        self.downloader = Downloader(
            dirs=self.dirs,
            url=self.url,
            url_to_crawl=self.url_to_crawl,
            interface=self.interface,
            images_size=self.configuration.images_size,
            images_quality=self.configuration.images_quality,
            ignore_downloads=self.ignore_downloads,
        )
        self.content_xpath = '//div[contains(@itemprop, "articleBody")]'
        self.images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
        self.content_cleanup_patterns = [
            '<span style="[^"]+"><i>Dyskretna Reklama</i></span>',
            '<span style="[^"]+"><br /><i>Koniec Dyskretnej Reklamy</i></span></div>',
        ]

    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def get_book_data(self) -> BookModel:
        pass


class Article:
    """
    Blog post, article which became book chapter...


    TODO: This class is a mess, all logic from here should be moved to crawler... but that's not that easy.
    """

    def __init__(self, url, html, crawler: AbstractCrawler):
        self.url = url
        self.html = html
        self.title = None
        self.tags: List[str] = []
        self.interface = crawler.interface
        self.dirs: DirModel = crawler.dirs
        self.comments = ""  # TODO: should be a list in the future
        self.content_xpath = crawler.content_xpath
        self.images_regex = crawler.images_regex
        self.language: Optional[str] = crawler.language
        self.images: List[str] = []
        self.images_captions: List[str] = []
        self.content = None
        self.date = None
        self.tree = None
        self.downloader = Downloader(
            dirs=self.dirs,
            url=self.url,
            url_to_crawl=crawler.url_to_crawl,
            interface=crawler.interface,
            images_size=crawler.configuration.images_size,
            images_quality=crawler.configuration.images_quality,
            ignore_downloads=crawler.ignore_downloads,
        )
        self.content_cleanup_xpath_patterns = ['//div[@class="post-footer"]']

    def get_title(self) -> str:
        if self.tree is not None:
            title = self.tree.xpath('//meta[@property="og:title"]/@content')
            if not title:
                title = self.tree.xpath('//*[@class="post-title entry-title"]/text()')
            title = title[0]
            return html.unescape(title.strip())
        return ""

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
            self.date = translate_month(self.date, self.language)
        try:
            self.date = dateutil.parser.parse(self.date)
        except IndexError:
            self.interface.print(f"Date not parsed: {self.date}")

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
        self.tree = fromstring(self.html)

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
        self.tree = fromstring(self.html)

    def set_content(self, content):
        self.content = content
        self.html = content
        self.tree = fromstring(self.html)

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
        content_element = self.tree.xpath(self.content_xpath)
        content_html = tostring(content_element[0], encoding="utf8")
        if isinstance(content_html, bytes):
            content_html = content_html.decode("utf8")
        content_html = content_html.replace("\n", "")
        content_html = re.sub(r'<a name=["\']more["\']/>', "", content_html)
        content_html = re.sub(r"<div[^>]*>", "<p>", content_html)
        content_html = content_html.replace("</div>", "")
        content = strip_tags(
            content_html,
            minify=True,
            keep_tags=["a", "img", "p", "i", "b", "strong", "ul", "ol", "li"],
        )
        content = re.sub(r"</i>[\s]*<i>", "", content)
        content = re.sub(r"</b>[\s]*<b>", "", content)
        return content

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

    def _content_cleanup_xpath(self):
        for p in self.content_cleanup_xpath_patterns:
            for bad in self.tree.xpath(p):
                bad.getparent().remove(bad)

    def process(self):
        self.tree = fromstring(self.html)
        self._content_cleanup_xpath()
        self.title = self.get_title()
        self.get_date()
        self.get_images()
        self.content = self.get_content()
        self.get_tags()
        self.get_comments()
