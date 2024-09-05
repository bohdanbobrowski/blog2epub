#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import re
from typing import Optional, List

import atoma  # type: ignore
from lxml.html.soupparser import fromstring
from pydantic import HttpUrl

from blog2epub.crawlers.abstract import AbstractCrawler
from blog2epub.common.book import Book
from blog2epub.models.book import BookModel, DirModel, ArticleModel, ImageModel
from blog2epub.models.configuration import ConfigurationModel


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
                output.append(self.article_class(art_urls[i], art_titles[i], self))
        else:
            articles_list = re.findall(self.articles_regex, content)
            for art in articles_list:
                output.append(self.article_class(art[0], art[1], self))
        return output

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

    def _articles_loop(self, content):
        for art in self._get_articles(content):
            self.article_counter += 1
            if not self.configuration.skip or (
                self.configuration.skip.isdigit()
                and self.article_counter > int(self.configuration.skip)
            ):
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
        if (
            self.configuration.limit
            and self.configuration.limit.isdigit()
            and len(self.articles) >= int(self.configuration.limit)
        ):
            self.url_to_crawl = None

    def _prepare_content(self, content):
        return content

    def crawl(self):
        self.active = True
        while self.url_to_crawl and not self.cancelled:
            content = self.downloader.get_content(self.url_to_crawl)
            tree = fromstring(content)
            self.language = self._get_blog_language(content)
            self.images = self.images + self._get_header_images(tree)
            self.description = self._get_blog_description(tree)
            self.title = self._get_blog_title(content)
            content = self._prepare_content(content)
            self._articles_loop(content)
            if not self.configuration.skip and len(self.articles) == 0:
                self._get_atom_content()
                self._atom_feed_loop()
            self.url_to_crawl = self._get_url_to_crawl(tree)
            self._check_limit()
        self.active = False
        self.subtitle = self._get_subtitle()

    def generate_ebook(
        self,
        articles: List[ArticleModel],
        destination_folder: str = ".",
        file_name: Optional[str] = None,
    ):
        if articles:
            self.book = Book(
                book_data=self,
                configuration=ConfigurationModel(
                    language=self.language or "en",
                ),
                interface=self.interface,
                destination_folder=destination_folder,
            )
            self.book.save(
                articles=articles,
                destination_folder=destination_folder,
                file_name=file_name,
            )
            return True
        else:
            self.interface.print("No articles found.")
            return False
