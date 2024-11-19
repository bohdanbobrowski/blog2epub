#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import html
import re
from typing import Tuple
from urllib import robotparser
from urllib.error import URLError
from urllib.parse import urljoin

import atoma  # type: ignore
import requests
from lxml import etree
from lxml.etree import XMLSyntaxError
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
                Pattern(xpath="//article"),
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
                Pattern(
                    xpath="//*[contains(@class, 'entry-title')]",
                ),
                Pattern(
                    xpath="//*[contains(@class, ' post-meta')]",
                ),
            ],
            title=[
                Pattern(
                    xpath='//*[contains(@class, "entry-title")]/text()',
                ),
                Pattern(
                    xpath='//*[contains(@class, "entry-title")]/a/text()',
                ),
                Pattern(
                    xpath='//*[contains(@class, "post-title")]/text()',
                ),
                Pattern(
                    xpath='//h1[contains(@class, "wp-block-post-title")]/text()',
                ),
                Pattern(
                    xpath='//meta[@property="og:title"]/@content',
                ),
                Pattern(
                    regex="<title>([^>^<]*)</title>",
                ),
            ],
            date=[
                Pattern(
                    xpath='//meta[@property="article:published_time"]/@content',
                ),
                Pattern(
                    xpath='//meta[@property="article:modified_time"]/@content',
                ),
                Pattern(
                    xpath='//abbr[@itemprop="datePublished"]/@title',
                ),
                Pattern(
                    xpath='//*[@class="date-header"]/span/text()',
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
                Pattern(
                    xpath="//article//img",
                ),
                Pattern(
                    xpath="//img[contains(@class, 'wp-post-image')]",
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

    def _get_blog_language(self, content: bytes | str) -> str:
        if isinstance(content, bytes):
            content = content.decode("utf-8")
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
        title = ""
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        if re.search("<title>([^>^<]*)</title>", content):
            title = re.search("<title>([^>^<]*)</title>", content).group(1).strip()  # type: ignore
            if len(title) > 60:
                if title.find("&#8211;") > -1:
                    title = title.split("&#8211;")[0].strip()
        return html.unescape(title)

    def _get_blog_description(self, tree) -> str:
        description = tree.xpath('//div[@id="header"]/div/div/div/p[@class="description"]/span/text()')
        if 0 in description:
            return description[0]
        else:
            return ""

    def _get_header_images(self, tree) -> list[ImageModel]:
        header_images = []
        xpaths = [
            '//*[contains(@class, "wp-block-image")]//img/@src',
            '//div[@id="header"]/div/div/div/p[@class="description"]/span/img/@src',
            "//img[contains(@class, 'wp-post-image')]/@src",
        ]
        for xpath in xpaths:
            for img in tree.xpath(xpath):
                img_obj = ImageModel(url=img)
                if self.downloader.download_image(img_obj):
                    header_images.append(img_obj)
        return header_images

    def _get_atom_content(self) -> bool:
        """Try to load atom"""
        atom_content = self.downloader.get_content(self.url + "/feeds/posts/default")
        self.atom_feed = atoma.parse_atom_bytes(atom_content)
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
        self.interface.print("Analysing sitemaps", end="")
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

    def _get_pages_from_blog_archive_widget(self) -> list[str] | None:
        """Addressing issue: https://github.com/bohdanbobrowski/blog2epub/issues/18"""
        page_content = self.downloader.get_content(self.url)
        pages = None
        if page_content is not None:
            page_tree = etree.fromstring(page_content)
            try:
                meta_url = str(page_tree.xpath("//meta/@content")[0])  # type: ignore
                meta_url = urljoin(self.url, meta_url.split("url=")[-1].strip())
                page_content = self.downloader.get_content(meta_url)
                if page_content:
                    try:
                        page_tree = etree.fromstring(page_content)
                    except XMLSyntaxError:
                        page_content = self._fix_html_tags(page_content)
                        page_tree = etree.fromstring(page_content)
                    pages = []
                    for _key, page in enumerate(page_tree.xpath('//div[contains(@class, "BlogArchive")]//a/@href')):  # type: ignore
                        if str(page).startswith(".."):
                            page_to_add = urljoin(self.url, str(page).lstrip("."))
                        else:
                            page_to_add = meta_url.replace("index.html", str(page))
                        if page_to_add not in pages:
                            pages.append(page_to_add)
            except IndexError:
                pass
        return pages

    def _fix_html_tags(self, content: bytes) -> bytes:
        str_content = content.decode()
        fixed_content = re.sub(r"([a-zA-Z0-9\-]+)=([a-zA-Z0-9\.\/\-\:#_]+)([>\s])", r'\1="\2"\3', str_content)  # type: ignore
        fixed_content = re.sub("<meta content=([^>]+)>", r"<meta content=\1 />", fixed_content)
        fixed_content = re.sub("<link href=([^>]+)>", r"<link href=\1 />", fixed_content)
        fixed_content = re.sub("<img ([^>]+)>", r"<img \1 />", fixed_content)
        fixed_content = fixed_content.replace("//>", "/>")
        fixed_content = fixed_content.replace("<br>", "<br/>")
        return fixed_content.encode()

    def _get_pages_urls(self, sitemap_url: str) -> list[str] | None:
        sitemap = requests.get(sitemap_url)
        pages = None
        if sitemap.status_code == 404:
            self.interface.print("")
            self.interface.print("Sitemap not found!")
            pages = self._get_pages_from_blog_archive_widget()
        if sitemap.status_code == 200:
            sitemap_pages = []
            for sitemap_element in etree.fromstring(sitemap.content):
                sitemap_element_children = sitemap_element.getchildren()  # type: ignore
                if sitemap_element_children:
                    sitemap_pages.append(sitemap_element_children[0].text)  # type: ignore
            sub_sitemaps, pages = self._check_for_sub_sitemaps(sitemap_pages)
            for sub_sitemap in sub_sitemaps:
                if (
                    re.search("sitemap.xml\\?page=[0-9]+$", sub_sitemap)
                    or re.search("wp-sitemap-posts-(post|page)-[0-9]+.xml$", sub_sitemap)
                    or re.search("(post|page)-sitemap[0-9-]*.xml$", sub_sitemap)
                ):
                    self.interface.print(".", end="")
                    pages += self._get_pages_from_sub_sitemap(sub_sitemap)
            self.interface.print("")
        if pages is not None:
            self.interface.print(f"Found {len(pages)} articles to crawl.")
            try:
                if int(self.configuration.skip) > 0:
                    pages = pages[int(self.configuration.skip) :]
                    self.interface.print(f"Skipping {self.configuration.skip} of them.")
            except ValueError:
                pass
        else:
            self.interface.print("No articles found!")
        return pages

    def _set_root_title(self, url: str | None = None):
        if not url:
            url = self.url
        if not self.title:
            html_content = self.downloader.get_content(url)
            if html_content is not None:
                tree = fromstring(html_content)
                self.language = self._get_blog_language(html_content)
                self.images = self.images + self._get_header_images(tree)
                self.description = self._get_blog_description(tree)
                self.title = self._get_blog_title(html_content)

    def crawl(self):
        self.interface.print(f"Starting {self.name}")
        self.active = True
        blog_pages = None
        try:
            sitemap_url = self._get_sitemap_url()
            blog_pages = self._get_pages_urls(sitemap_url)
        except URLError:
            self.cancelled = True
            self.interface.print(f"Networking error: {self.url}")
        if blog_pages:
            self._set_root_title()
            for page_url in blog_pages:
                html_content = self.downloader.get_content(page_url)
                self._set_root_title(page_url)
                art_factory = self.article_factory_class(
                    url=page_url,
                    html_content=html_content,
                    patterns=self.patterns,
                    interface=self.interface,
                    dirs=self.dirs,
                    language=self.language,
                    downloader=self.downloader,
                    download_callback=self._break_the_loop,
                    blog_title=self.title,
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
