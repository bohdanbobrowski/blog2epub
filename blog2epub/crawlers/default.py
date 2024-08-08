#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import gzip
import hashlib
import html
import imghdr
import logging
import os
import re
import time
from datetime import datetime
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

import atoma
import dateutil.parser
import requests
from lxml.ElementInclude import etree
from lxml.html.soupparser import fromstring
from PIL import Image
from pydantic import HttpUrl

from blog2epub.crawlers.abstract import AbstractCrawler
from blog2epub.common.book import Book
from blog2epub.common.crawler import (
    prepare_file_name,
    prepare_port,
    prepare_url,
    prepare_url_to_crawl,
)
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import BookModel, DirModel, ArticleModel, ImageModel


class DefaultCrawler(AbstractCrawler):
    """
    Universal blog crawler.
    """

    article_class = "Article"

    content_xpath = (
        "//div[contains(concat(' ',normalize-space(@class),' '),'post-body')]"
    )
    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
    articles_regex = r"<h3 class=\'post-title entry-title\' itemprop=\'name\'>[\s]*<a href=\'([^\']*)\'>([^>^<]*)</a>[\s]*</h3>"

    ignore_downloads = []

    def __init__(
        self,
        url,
        include_images: bool = True,
        images_size: tuple = (600, 800),
        images_quality: int = 40,
        start=None,
        end=None,
        limit: int = None,
        skip: int = None,
        force_download: bool = False,
        file_name: str = None,
        destination_folder: str = "./",
        cache_folder: str = None,
        language: str = None,
        interface=None,
    ):
        self.url = prepare_url(url)
        self.url_to_crawl = prepare_url_to_crawl(self.url)
        self.port = prepare_port(self.url_to_crawl)
        self.file_name = prepare_file_name(file_name, self.url)
        self.destination_folder = destination_folder
        self.cache_folder = cache_folder
        if cache_folder is None:
            self.cache_folder = os.path.join(str(Path.home()), ".blog2epub")
        self.include_images = include_images
        self.images_quality = images_quality
        self.images_size = images_size
        self.start = start
        self.end = end
        self.limit = limit
        self.skip = skip
        self.force_download = force_download
        self.interface = self._get_the_interface(interface)
        self.dirs = Dirs(self.cache_folder, self.url.replace("/", "_"))
        self.book = None
        self.title = None
        self.subtitle = None
        self.description = None
        self.language = language
        self.atom_feed = False
        self.articles = []
        self.article_counter = 0
        self.images = []
        self.downloader = Downloader(self)
        self.tags = {}
        self.active = False
        self.cancelled = False

    def _get_articles_list(self) -> List[ArticleModel]:
        """This is temporary solution - crawler should use data models as default data storage."""
        articles_list = []
        for article in self.articles:
            articles_list.append(
                ArticleModel(
                    url=HttpUrl(article.url),
                    title=article.title,
                    date=article.date,
                    content=article.content,
                    comments=article.comments,
                )
            )
        return articles_list

    def _get_images(self) -> List[ImageModel]:
        """This is temporary solution - crawler should use data models as default data storage."""
        images_list = []
        for article in self.articles:
            for key, image in enumerate(article.images):
                description = ""
                if key in article.images_captions:
                    description = article.images_captions[key]
                images_list.append(
                    ImageModel(url="", hash=image, description=description)
                )
        return images_list

    def get_book_data(self) -> BookModel:
        """This is temporary solution - crawler should use data models as default data storage."""
        book_data = BookModel(
            url=self.url,
            title=self.title,
            subtitle=self.subtitle,
            description=self.description,
            dirs=DirModel(
                path=self.dirs.path,
                html=self.dirs.html,
                images=self.dirs.images,
                originals=self.dirs.originals,
            ),
            articles=self._get_articles_list(),
            images=self._get_images(),
            start=self.start,
            end=self.end,
            file_name_prefix=self.file_name,
            destination_folder=self.destination_folder,
            cover=None,
            cover_image_path=None,
        )
        return book_data

    @staticmethod
    def _get_the_interface(interface):
        if interface:
            return interface
        return EmptyInterface()

    def _get_subtitle(self):
        if self.end is None:
            return self.start.strftime("%d %B %Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.end.strftime("%d") + "-" + self.start.strftime("%d %B %Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.end.strftime("%d %B") + " - " + self.start.strftime("%d %B %Y")
        return self.end.strftime("%d %B %Y") + " - " + self.start.strftime("%d %B %Y")

    def get_cover_title(self):
        cover_title = self.title + " "
        if self.start == self.end:
            cover_title = cover_title + str(self.start)
        else:
            end_date = self.end.split(" ")
            start_date = self.start.split(" ")
            if len(end_date) == len(start_date):
                ed = []
                for i, d in enumerate(end_date):
                    if d != start_date[i]:
                        ed.append(d)
            ed = " ".join(ed)
            cover_title = cover_title + ed + "-" + self.start
        return cover_title

    @staticmethod
    def get_date(str_date):
        return re.sub(r"[^\,]*, ", "", str_date)

    def _set_blog_language(self, content):
        if self.language is None and re.search(r"'lang':[\s]*'([a-z^']+)'", content):
            self.language = (
                re.search(r"'lang':[\s]*'([a-z^']+)'", content).group(1).strip()
            )
        if self.language is None and re.search(r"lang=['\"]([a-z]+)['\"]", content):
            self.language = (
                re.search(r"lang=['\"]([a-z]+)['\"]", content).group(1).strip()
            )
        if self.language is None and re.search(
            r"locale['\"]:[\s]*['\"]([a-z]+)['\"]", content
        ):
            self.language = (
                re.search(r"locale['\"]:[\s]*['\"]([a-z]+)['\"]", content)
                .group(1)
                .strip()
            )
        if self.language is None:
            self.language = "en"

    def _get_blog_title(self, content):
        if re.search("<title>([^>^<]*)</title>", content):
            return re.search("<title>([^>^<]*)</title>", content).group(1).strip()
        return ""

    def _get_blog_description(self, tree) -> Optional[str]:
        description = tree.xpath(
            '//div[@id="header"]/div/div/div/p[@class="description"]/span/text()'
        )
        if 0 in description:
            return description[0]
        else:
            return None

    def _get_header_images(self, tree):
        header_images = []
        for img in tree.xpath(
            '//div[@id="header"]/div/div/div/p[@class="description"]/span/img/@src'
        ):
            header_images.append(self.downloader.download_image(img))
        return header_images

    def _get_articles(self, content):
        """
        :param content: web page content
        :return: list of Article class objects
        """
        tree = fromstring(content)
        art_urls = tree.xpath("//h3[contains(@class, 'entry-title')]/a/@href")
        art_titles = tree.xpath("//h3[contains(@class, 'entry-title')]/a/text()")
        output = []
        if art_urls and len(art_urls) == len(art_titles):
            for i in range(len(art_urls)):
                output.append(
                    eval(self.article_class)(art_urls[i], art_titles[i], self)
                )
        else:
            articles_list = re.findall(self.articles_regex, content)
            for art in articles_list:
                output.append(eval(self.article_class)(art[0], art[1], self))
        return output

    def _get_atom_content(self) -> bool:
        """Try to load atom"""
        atom_content = self.downloader.get_content(
            "https://" + self.url + "/feeds/posts/default"
        )
        self.atom_feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))
        return True

    def _get_url_to_crawl(self, tree) -> str:
        url_to_crawl = None
        if tree.xpath('//a[@class="blog-pager-older-link"]/@href'):
            url_to_crawl = tree.xpath('//a[@class="blog-pager-older-link"]/@href')[0]
        return url_to_crawl

    def _add_tags(self, tags) -> None:
        for tag in tags:
            if tag in self.tags:
                self.tags[tag] = self.tags[tag] + 1
            else:
                self.tags[tag] = 1

    def _atom_feed_loop(self):
        self.url_to_crawl = None
        for item in self.atom_feed.entries:
            try:
                self.article_counter += 1
                art = eval(self.article_class)(
                    item.links[0].href, item.title.value, self
                )
                if self.skip and self.article_counter < self.skip:
                    self.interface.print("[skipping] " + art.title)
                    continue
                art_no = len(self.articles) + 1
                self.interface.print(f"{art_no}. {art.title}")
                art.date = item.updated
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                if item.content:
                    art.set_content(item.content.value)
                art.get_images()
                art.set_content(art.html)
                self.images = self.images + art.images
                self.articles.append(art)
                self._add_tags(art.tags)
                if self.limit and len(self.articles) >= self.limit:
                    break
            except AttributeError as e:
                self.interface.print(str(e))
                self.interface.print("[article not recognized - skipping]")

    def _articles_loop(self, content):
        for art in self._get_articles(content):
            self.article_counter += 1
            if not self.skip or self.article_counter > self.skip:
                art.process()
                self.images = self.images + art.images
                self.interface.print(str(len(self.articles) + 1) + ". " + art.title)
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                self.articles.append(art)
                self._add_tags(art.tags)
                self._check_limit()
            else:
                self.interface.print("[skipping] " + art.title)
            if not self.url_to_crawl:
                break

    def _check_limit(self):
        if self.limit and len(self.articles) >= self.limit:
            self.url_to_crawl = None

    def _prepare_content(self, content):
        return content

    def crawl(self):
        self.active = True
        while self.url_to_crawl and not self.cancelled:
            content = self.downloader.get_content(self.url_to_crawl)
            tree = fromstring(content)
            self._set_blog_language(content)
            self.images = self.images + self._get_header_images(tree)
            self.description = self._get_blog_description(tree)
            self.title = self._get_blog_title(content)
            content = self._prepare_content(content)
            self._articles_loop(content)
            if not self.skip and len(self.articles) == 0:
                self._get_atom_content()
                self._atom_feed_loop()
            self.url_to_crawl = self._get_url_to_crawl(tree)
            self._check_limit()
        self.active = False
        self.subtitle = self._get_subtitle()

    def generate_ebook(
        self,
        articles: List[int],
        destination_folder: Optional[str],
        file_name: Optional[str] = None,
    ):
        if articles:
            self.book = Book(self)
            self.book.save(
                articles=articles,
                destination_folder=destination_folder,
                file_name=file_name,
            )
            return True
        else:
            self.interface.print("No articles found.")
            return False


class Dirs:
    """
    Tiny class to temporary directories configurations.
    """

    def prepare_directories(self):
        paths = [self.html, self.images, self.originals]
        for p in paths:
            if not os.path.exists(p):
                os.makedirs(p)

    def __init__(self, cache_folder, name):
        self.path = os.path.join(cache_folder, name)
        self.html = os.path.join(self.path, "html")
        self.images = os.path.join(self.path, "images")
        self.originals = os.path.join(self.path, "originals")
        self.prepare_directories()


class Downloader:
    def __init__(self, crawler):
        self.dirs = crawler.dirs
        self.url_to_crawl = crawler.url_to_crawl
        self.crawler_url = crawler.url
        self.crawler_port = crawler.port
        self.interface = crawler.interface
        self.force_download = crawler.force_download
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
        self.dirs.prepare_directories()
        try:
            response = self.session.get(url, cookies=self.cookies, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return None
        self.cookies = response.cookies
        data = response.content
        contents = data.decode("utf-8")
        self.file_write(contents, filepath)
        return contents

    def image_download(self, url: str, filepath: str) -> bool:
        if self._is_url_in_ignored(url):
            return None
        self.dirs.prepare_directories()
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
            if self.force_download or (
                not os.path.isfile(filepath) and not os.path.isfile(filepath + ".gz")
            ):
                contents = self.file_download(url, filepath)
            else:
                contents = self.file_read(filepath)
            if contents is not None:
                break
            self.interface.print(f"...repeat request: {url}")
            time.sleep(3)
        if contents is not None:
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
        if not os.path.isfile(resized_fn) or self.force_download:
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
                picture.thumbnail(self.images_size, Image.LANCZOS)
            picture = picture.convert("L")
            picture.save(resized_fn, format="JPEG", quality=self.images_quality)
            os.remove(original_fn)
            return img_hash + ".jpg"
        return None


class Article:
    """
    Blog post, article which became book chapter...
    """

    def __init__(self, url, title, crawler):
        self.url = url
        self.title = title
        self.tags = []
        self.interface = crawler.interface
        self.dirs = crawler.dirs
        self.comments = ""  # TODO: should be a list in the future
        self.content_xpath = crawler.content_xpath
        self.images_regex = crawler.images_regex
        self.language = crawler.language
        self.images = []
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
