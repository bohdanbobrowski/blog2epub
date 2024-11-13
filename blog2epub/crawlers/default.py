#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import re
from typing import Optional, Tuple
from urllib import robotparser
from urllib.parse import urljoin

import atoma  # type: ignore
import requests
from lxml import etree
from lxml.html.soupparser import fromstring

from blog2epub.common.downloader import Downloader
from blog2epub.crawlers.abstract import AbstractCrawler
from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import BookModel, DirModel, ImageModel
from blog2epub.models.content_patterns import ContentPatterns, Pattern


class DefaultCrawler(AbstractCrawler):
    """
    Universal blog crawler.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "default crawler"
        self.article_factory_class = DefaultArticleFactory
        self.patterns = ContentPatterns(
            content=[
                Pattern(xpath='//div[contains(@itemprop, "articleBody")]'),
                Pattern(xpath='//section[contains(@itemprop, "text")]'),
                Pattern(xpath='//div[contains(@class, "entry-content")]'),
                Pattern(xpath='//section[contains(@class, "entry-content")]'),
                Pattern(xpath='//div[@id="content"]'),
            ],
            content_cleanup=[
                Pattern(
                    regex=r'<span style="[^"]+"><i>Dyskretna Reklama</i></span>',
                ),
                Pattern(
                    regex=r'<span style="[^"]+"><br /><i>Koniec Dyskretnej Reklamy</i></span></div>',
                ),
                Pattern(
                    xpath='//div[@class="post-footer"]',
                ),
            ],
            title=[
                Pattern(
                    xpath='//meta[@property="og:title"]/@content',
                ),
                Pattern(
                    xpath='//*[contains(@class, "entry-title")]/text()',
                ),
                Pattern(
                    xpath='//*[contains(@class, "post-title")]/text()',
                ),
                Pattern(
                    xpath='//h1[contains(@class, "wp-block-post-title")]/text()',
                ),
            ],
            date=[
                Pattern(
                    xpath='//abbr[@itemprop="datePublished"]/@title',
                ),
                Pattern(
                    xpath='//*[@class="date-header"]/span/text()',
                ),
                Pattern(
                    xpath='//meta[@property="article:published_time"]/@content',
                ),
                Pattern(
                    xpath='//meta[@property="article:modified_time"]/@content',
                ),
                Pattern(xpath='//time[@property="datetime"]/@content'),
                Pattern(xpath="//time/@text"),
            ],
            images=[
                Pattern(
                    xpath='//div[contains(@class, "header section")]//img',
                ),
                Pattern(
                    xpath='//div[contains(@itemprop, "articleBody")]//img',
                ),
                Pattern(
                    xpath='//figure[contains(@class, "wp-block-post-featured-image")]//img',
                ),
                Pattern(
                    xpath='//div[contains(@class, "entry-content")]//img',
                ),
                Pattern(
                    xpath='//section[contains(@class, "entry-content")]//img',
                ),
                Pattern(
                    xpath='//section[contains(@class, "article-header")]//img',
                ),
                Pattern(
                    xpath='//div[@id="content"]//img',
                ),
            ],
        )
        self.downloader = Downloader(
            dirs=self.dirs,
            url=self.url,
            interface=self.interface,
            images_size=self.configuration.images_size,
            images_quality=self.configuration.images_quality,
            ignore_downloads=self.ignore_downloads,
        )

    def get_book_data(self) -> BookModel:
        """This is temporary solution - crawler should use data models as default data storage."""
        images_list = [im for art in self.articles for im in art.images] + self.images  # this is mind-blowing
        images_set = set(images_list)
        images_list = list(images_set)
        book_data = BookModel(
            url=self.url,
            title=self.title,
            subtitle=self.subtitle,
            description=self.description,
            dirs=DirModel(path=self.dirs.path),
            articles=self.articles,
            images=images_list,
            start=self.start,
            end=self.end,
            file_name_prefix=self.file_name,
            destination_folder=self.configuration.destination_folder,
            cover=None,
            cover_image_path=None,
        )
        return book_data

    @staticmethod
    def get_date(str_date):
        return re.sub(r"[^\,]*, ", "", str_date)

    def _get_blog_language(self, content) -> str:
        regex_patterns = [
            r"'lang':[\s]*'([a-z^']+)'",
            r"lang=['\"]([a-z]+)['\"]",
            r"locale['\"]:[\s]*['\"]([a-z]+)['\"]",
        ]
        for r_pat in regex_patterns:
            r_result = re.search(r_pat, content)
            if r_result:
                return r_result.group(1).strip()
        return "en"

    def _get_blog_title(self, content: str | bytes) -> str:
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        if re.search("<title>([^>^<]*)</title>", content):
            return re.search("<title>([^>^<]*)</title>", content).group(1).strip()
        return ""

    def _get_blog_description(self, tree) -> Optional[str]:
        description = tree.xpath('//div[@id="header"]/div/div/div/p[@class="description"]/span/text()')
        if 0 in description:
            return description[0]
        else:
            return None

    def _get_header_images(self, tree) -> list[ImageModel]:
        header_images = []
        for img in tree.xpath('//div[@id="header"]/div/div/div/p[@class="description"]/span/img/@src'):
            img_obj = ImageModel(url=img)
            self.downloader.download_image(img_obj)
            header_images.append(img_obj)
        return header_images

    def _get_atom_content(self) -> bool:
        """Try to load atom"""
        atom_content = self.downloader.get_content(self.url + "/feeds/posts/default")
        self.atom_feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))
        return True

    def _add_tags(self, tags) -> None:
        for tag in tags:
            if tag in self.tags:
                self.tags[tag] = self.tags[tag] + 1
            else:
                self.tags[tag] = 1

    def _break_the_loop(self):
        if (
            self.cancelled
            or self.configuration.limit
            and self.configuration.limit.isdigit()
            and len(self.articles) >= int(self.configuration.limit)
        ):
            return True
        return False

    def _get_sitemap_url(self) -> str:
        robots_parser = robotparser.RobotFileParser()
        robots_parser.set_url(urljoin(self.url, "/robots.txt"))
        robots_parser.read()
        if hasattr(robots_parser, "sitemaps") and robots_parser.sitemaps:
            sitemap_url = robots_parser.sitemaps[0]
        else:
            sitemap_url = urljoin(self.url, "/sitemap.xml")
        return sitemap_url

    def _get_pages_from_sub_sitemap(self, sitemap_url: str) -> list[str]:
        sub_sitemap = requests.get(sitemap_url)
        pages = []
        for element in etree.fromstring(sub_sitemap.content):  # type: ignore
            page_url = element.getchildren()[0].text  # type: ignore
            if page_url.strip("/") != self.url.strip("/"):
                pages.append(page_url)
        return pages

    @staticmethod
    def _check_for_sub_sitemaps(
        sitemap_pages: list[str],
    ) -> Tuple[list[str], list[str]]:
        sub_sitemaps = []
        pages = []
        for element in sitemap_pages:
            if element.endswith(".xml") or re.search("sitemap.xml\\?page=[0-9]+$", element):
                sub_sitemaps.append(element)
            else:
                pages.append(element)
        return sub_sitemaps, pages

    def _get_pages_urls(self, sitemap_url: str) -> list[str]:
        sitemap = requests.get(sitemap_url)
        sitemap_pages = []
        for sitemap_element in etree.fromstring(sitemap.content):  # type: ignore
            sitemap_element_children = sitemap_element.getchildren()
            if sitemap_element_children:
                sitemap_pages.append(sitemap_element_children[0].text)  # type: ignore
        sub_sitemaps, pages = self._check_for_sub_sitemaps(sitemap_pages)
        for sub_sitemap in sub_sitemaps:
            if (
                re.search("sitemap.xml\\?page=[0-9]+$", sub_sitemap)
                or re.search("wp-sitemap-posts-(post|page)-[0-9]+.xml$", sub_sitemap)
                or re.search("(post|page)-sitemap[0-9-]*.xml$", sub_sitemap)
            ):
                pages += self._get_pages_from_sub_sitemap(sub_sitemap)
        self.interface.print(f"Found {len(pages)} articles to crawl.")
        return pages

    def _set_root_title(self):
        if not self.title:
            html_content = self.downloader.get_content(self.url)
            tree = fromstring(html_content)
            self.language = self._get_blog_language(html_content)
            self.images = self.images + self._get_header_images(tree)
            self.description = self._get_blog_description(tree)
            self.title = self._get_blog_title(html_content)

    def crawl(self):
        self.interface.print(f"Starting {self.name}")
        self.active = True
        sitemap_url = self._get_sitemap_url()
        blog_pages = self._get_pages_urls(sitemap_url)
        if blog_pages:
            for page_url in blog_pages:
                html_content = self.downloader.get_content(page_url)
                self._set_root_title()
                art_factory = self.article_factory_class(
                    url=page_url,
                    html_content=html_content,
                    patterns=self.patterns,
                    interface=self.interface,
                    dirs=self.dirs,
                    language=self.language,
                    downloader=self.downloader,
                )
                art = art_factory.process()
                self.images = self.images + art.images
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                self.articles.append(art)
                self.interface.print(f"{len(self.articles)}. {art.title}")
                if self._break_the_loop():
                    break
        self.active = False
