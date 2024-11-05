#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import re
import requests
from urllib.parse import urljoin
from urllib import robotparser
from typing import Optional, List

import atoma  # type: ignore
from lxml.html.soupparser import fromstring
from lxml import etree

from blog2epub.crawlers.abstract import AbstractCrawler
from blog2epub.models.book import BookModel, DirModel, ArticleModel, ImageModel


class DefaultCrawler(AbstractCrawler):
    """
    Universal blog crawler.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_articles_list(self) -> List[ArticleModel]:
        """This is temporary solution - crawler should use data models as default data storage."""
        articles_list = []
        for article in self.articles:
            articles_list.append(
                ArticleModel(
                    url=article.url,
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
            dirs=DirModel(path=self.dirs.path),
            articles=self._get_articles_list(),
            images=self._get_images(),
            start=self.start,
            end=self.end,
            file_name_prefix=self.file_name,
            destination_folder=self.configuration.destination_folder,
            cover=None,
            cover_image_path=None,
        )
        return book_data

    def _get_subtitle(self):
        if self.end is None:
            return self.start.strftime("%d.%B.%Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.end.strftime("%d") + "-" + self.start.strftime("%d.%B.%Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.end.strftime("%d.%B") + " - " + self.start.strftime("%d.%B.%Y")
        return self.end.strftime("%d.%B.%Y") + " - " + self.start.strftime("%d.%B.%Y")

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

    def _get_atom_content(self) -> bool:
        """Try to load atom"""
        atom_content = self.downloader.get_content(
            "https://" + self.url + "/feeds/posts/default"
        )
        self.atom_feed = atoma.parse_atom_bytes(bytes(atom_content, encoding="utf-8"))
        return True

    def _get_url_to_crawl(self, tree) -> str | None:
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
                art = self.article_class(item.links[0].href, item.title.value, self)
                if (
                    self.configuration.skip
                    and self.configuration.skip.isdigit()
                    and self.article_counter < int(self.configuration.skip)
                ):
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
                if self.configuration.limit and len(self.articles) >= int(
                    self.configuration.limit
                ):
                    break
            except AttributeError as e:
                self.interface.print(str(e))
                self.interface.print("[article not recognized - skipping]")

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
        if robots_parser.sitemaps:
            sitemap_url = robots_parser.sitemaps[0]
        else:
            sitemap_url = urljoin(self.url, "/sitemap.xml")
        return sitemap_url

    def _get_pages_urls(self, sitemap_url: str) -> list[str]:
        sitemap = requests.get(sitemap_url)
        sitemap_root = etree.fromstring(sitemap.content)
        pages = []
        for sitemap in sitemap_root:
            pages.append(sitemap.getchildren()[0].text)
        self.interface.print(f"Found {len(pages)} articles to crawl.")
        return pages

    def crawl(self):
        self.active = True
        sitemap_url = self._get_sitemap_url()
        blog_pages = self._get_pages_urls(sitemap_url)
        if blog_pages:
            for page_url in blog_pages:
                content = self.downloader.get_content(page_url)
                if not self.title:
                    tree = fromstring(content)
                    self.language = self._get_blog_language(content)
                    self.images = self.images + self._get_header_images(tree)
                    self.description = self._get_blog_description(tree)
                    self.title = self._get_blog_title(content)
                art = self.article_class(page_url, content, self)
                art.process()
                self.images = self.images + art.images
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                self.articles.append(art)
                self.interface.print(f"{len(self.articles)}. {art.title}")
                if self._break_the_loop():
                    break
        else:
            self._get_atom_content()
            self._atom_feed_loop()
        self.active = False
        self.subtitle = self._get_subtitle()
