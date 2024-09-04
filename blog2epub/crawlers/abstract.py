import html
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from xml import etree
import gzip
import hashlib
import imghdr
import re
import time
from http.cookiejar import CookieJar
from urllib.parse import urlparse

import requests
from lxml.html.soupparser import fromstring
from PIL import Image

from blog2epub.common.downloader import prepare_directories
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
    ignore_downloads: List[str] = []

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
        self.downloader = Downloader(self)
        self.tags: Dict = {}
        self.active = False
        self.cancelled = False

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


class Downloader:
    def __init__(self, crawler):
        self.dirs = crawler.dirs
        self.url_to_crawl = crawler.url_to_crawl
        self.crawler_url = crawler.url
        self.crawler_port = crawler.port
        self.interface = crawler.interface
        self.images_size = crawler.images_size
        self.images_quality = crawler.images_quality
        self.ignore_downloads = crawler.ignore_downloads
        self.cookies = CookieJar()
        self.session = requests.session()
        self.headers = {}

    def get_urlhash(self, url):
        m = hashlib.md5()
        m.update(url.encode("utf-8"))
        return m.hexdigest()

    def file_write(self, contents, filepath):
        filepath = filepath + ".gz"
        with gzip.open(filepath, "wb") as f:
            f.write(contents.encode("utf-8"))

    def file_read(self, filepath):
        if os.path.isfile(filepath + ".gz"):
            with gzip.open(filepath + ".gz", "rb") as f:
                contents = f.read().decode("utf-8")
        else:
            with open(filepath, "rb") as html_file:
                contents = html_file.read().decode("utf-8")
            self.file_write(contents, filepath)
            os.remove(filepath)
        return contents

    def get_filepath(self, url):
        return os.path.join(self.dirs.html, self.get_urlhash(url) + ".html")

    def _is_url_in_ignored(self, url) -> bool:
        for search_rule in self.ignore_downloads:
            if re.match(search_rule, url):
                return True
        return False

    def file_download(self, url: str, filepath: str) -> Optional[str]:
        if self._is_url_in_ignored(url):
            return None
        prepare_directories(self.dirs)
        try:
            response = self.session.get(url, cookies=self.cookies, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return None
        self.cookies = response.cookies
        data = response.content
        contents = data.decode("utf-8")
        self.file_write(contents, filepath)
        return contents

    def image_download(self, url: str, filepath: str) -> bool | None:
        if self._is_url_in_ignored(url):
            return None
        prepare_directories(self.dirs)
        try:
            response = self.session.get(url, cookies=self.cookies, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return False
        with open(filepath, "wb") as f:
            f.write(response.content)
        time.sleep(1)
        return True

    def checkInterstitial(self, contents):
        interstitial = re.findall('interstitial=([^"]+)', contents)
        if interstitial:
            return interstitial[0]
        return False

    def get_content(self, url):
        # TODO: This needs refactor!
        filepath = self.get_filepath(url)
        for x in range(0, 3):
            if not os.path.isfile(filepath) and not os.path.isfile(filepath + ".gz"):
                contents = self.file_download(url, filepath)
            else:
                contents = self.file_read(filepath)
            if contents is not None:
                break
            self.interface.print(f"...repeat request: {url}")
            time.sleep(3)
        if contents:
            interstitial = self.checkInterstitial(contents)
            if interstitial:
                interstitial_url = (
                    "http://" + self.crawler_url + "?interstitial=" + interstitial
                )
                self.file_download(
                    interstitial_url, self.get_filepath(interstitial_url)
                )
                contents = self.file_download(
                    "http://" + self.crawler_url,
                    self.get_filepath("http://" + self.crawler_url),
                )
        return contents

    def _fix_image_url(self, img: str) -> str:
        if not img.startswith("http"):
            uri = urlparse(self.url_to_crawl)
            if uri.netloc not in img:
                img = os.path.join(uri.netloc, img)
            while not img.startswith("//"):
                img = "/" + img
            img = f"{uri.scheme}:{img}"
        return img

    def download_image(self, img: str) -> Optional[str]:
        img = self._fix_image_url(img)
        img_hash = self.get_urlhash(img)
        img_type = os.path.splitext(img)[1].lower()
        if img_type not in [".jpeg", ".jpg", ".png", ".bmp", ".gif", ".webp"]:
            return None
        original_fn = os.path.join(self.dirs.originals, img_hash + "." + img_type)
        resized_fn = os.path.join(self.dirs.images, img_hash + ".jpg")
        if os.path.isfile(resized_fn):
            return img_hash + ".jpg"
        if not os.path.isfile(resized_fn):
            self.image_download(img, original_fn)
        if os.path.isfile(original_fn):
            original_img_type = imghdr.what(original_fn)
            if original_img_type is None:
                os.remove(original_fn)
                return None
            picture = Image.open(original_fn)
            if (
                picture.size[0] > self.images_size[0]
                or picture.size[1] > self.images_size[1]
            ):
                picture.thumbnail(self.images_size, Image.LANCZOS)  # type: ignore
            converted_picture = picture.convert("L")
            converted_picture.save(
                resized_fn, format="JPEG", quality=self.images_quality
            )
            os.remove(original_fn)
            return img_hash + ".jpg"
        return None
