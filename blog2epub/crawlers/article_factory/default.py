import html
import re
from datetime import datetime
from typing import Optional

import dateutil
from lxml.etree import tostring
from lxml.html.soupparser import fromstring
from strip_tags import strip_tags  # type: ignore

from blog2epub.common.language_tools import translate_month
from blog2epub.crawlers.article_factory.abstract import AbstractArticleFactory
from blog2epub.models.book import ArticleModel, ImageModel


class DefaultArticleFactory(AbstractArticleFactory):
    def get_title(self) -> Optional[str]:
        if self.tree is not None and self.patterns is not None:
            for title_pattern in self.patterns.title:
                if title_pattern.xpath:
                    title = self.tree.xpath(title_pattern.xpath)
                    if len(title) > 0:
                        title = title[0]
                        return html.unescape(title.strip())
        return None

    def get_date(self) -> Optional[datetime]:
        result_date = None
        if self.patterns is not None:
            for date_pattern in self.patterns.date:
                if date_pattern.xpath:
                    date = self.tree.xpath(date_pattern.xpath)
                    if len(date) > 0:
                        result_date = date[0]
        if result_date is None:
            d = self.url.split("/")
            if len(d) > 4:
                result_date = f"{d[3]}-{d[4]}-01 00:00"
            else:
                result_date = str(datetime.now())
        else:
            result_date = translate_month(result_date, self.language)  # type: ignore
        try:
            return dateutil.parser.parse(result_date)  # type: ignore
        except (IndexError, dateutil.parser.ParserError):  # type: ignore
            pass
        return None

    def _find_images(self):
        images = []
        if self.patterns:
            for pattern in self.patterns.images:
                images += re.findall(pattern.regex, self.html)
        return images

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
        im_regex = '<a href="' + img.replace("+", r"\+") + '" imageanchor="1"[^<]*<img.*?></a>'
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    @staticmethod
    def _bloggerphoto_ripper(img: str, img_hash: str, art_html: str) -> str:
        im_regex = '<a href="[^"]+"><img.*?id="BLOGGER_PHOTO_ID_[0-9]+".*?src="' + img.replace("+", r"\+") + '".*?/a>'
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    @staticmethod
    def _img_ripper(img, img_hash, art_html):
        im_regex = '<img.*?src="' + img.replace("+", r"\+") + '".*?>'
        return re.sub(im_regex, " #blog2epubimage#" + img_hash + "# ", art_html)

    def process_images(self, images, ripper) -> list[ImageModel]:
        images_list = []
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
                    images_list.append(
                        ImageModel(
                            hash=img_hash,
                            url=img,
                            description=caption,
                        )
                    )
        self.tree = fromstring(self.html)
        return images_list

    def get_images(self):
        # TODO: needs refacor!
        images_list = []
        images_list += self.process_images(self._find_images(), self._default_ripper)
        images_list += self.process_images(self.tree.xpath('//a[@imageanchor="1"]/@href'), self._nocaption_ripper)
        images_list += self.process_images(
            self.tree.xpath('//img[contains(@id,"BLOGGER_PHOTO_ID_")]/@src'),
            self._bloggerphoto_ripper,
        )
        images_list += self.process_images(self.tree.xpath("//img/@src"), self._img_ripper)
        self.replace_images(images_list)
        self.tree = fromstring(self.html)
        return images_list

    def set_content(self, content):
        self.content = content
        self.html = content
        self.tree = fromstring(self.html)

    def replace_images(self, images_list: list[ImageModel]):
        for image in images_list:
            image_html = (
                '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/'
                + image.file_name
                + '" /></td></tr><tr><td class="tr-caption" style="text-align: center;">'
                + image.description
                + "</td></tr></tbody></table>"
            )
            self.html = self.html.replace("#blog2epubimage#" + image.hash + "#", image_html)

    def get_content(self) -> str:
        content = ""
        if self.patterns:
            for pattern in self.patterns.content:
                if pattern.xpath:
                    content_element = self.tree.xpath(pattern.xpath)
                    if content_element:
                        content_html = tostring(content_element[0]).decode("utf8")
                        content_html = content_html.replace("\n", "")
                        content_html = re.sub(r'<a name=["\']more["\']/>', "", content_html)
                        content_html = re.sub(r"<div[^>]*>", "<p>", content_html)
                        content_html = content_html.replace("</div>", "")
                        content = strip_tags(
                            content_html,
                            minify=True,
                            keep_tags=[
                                "a",
                                "img",
                                "p",
                                "i",
                                "b",
                                "strong",
                                "ul",
                                "ol",
                                "li",
                                "br",
                            ],
                        )
                        content = re.sub(r"</i>[\s]*<i>", "", content)
                        content = re.sub(r"</b>[\s]*<b>", "", content)
                if content:
                    return content
        return content

    def get_tags(self):
        tags = self.tree.xpath('//a[@rel="tag"]//text()')
        output = []
        for t in tags:
            t = t.strip()
            output.append(t)
        self.tags = output

    def get_comments(self) -> str:
        headers = self.tree.xpath('//div[@id="comments"]/h4/text()')
        result_comments = ""
        if len(headers) == 1:
            return_comments = "<hr/><h3>" + headers[0] + "</h3>"
        comments_in_article = self.tree.xpath('//div[@class="comment-block"]//text()')
        if comments_in_article:
            tag = "h4"
            for c in comments_in_article:
                c = c.strip()
                if c not in ("Odpowiedz", "Usuń"):
                    return_comments = return_comments + "<" + tag + ">" + c + "</" + tag + ">"
                    if tag == "h4":
                        tag = "p"
                if c == "Usuń":
                    tag = "h4"
        else:
            authors = self.tree.xpath('//dl[@id="comments-block"]//*[@class="comment-author"]')
            comments = self.tree.xpath('//dl[@id="comments-block"]//*[@class="comment-body"]')
            try:
                for x in range(0, len(authors) + 1):
                    a = "".join(authors[x].xpath(".//text()")).strip().replace("\n", " ")
                    c = "".join(comments[x].xpath(".//text()")).strip()
                    return_comments += f"<h4>{a}</h4>"
                    return_comments += f"<p>{c}</p>"
            except IndexError:
                pass
        return result_comments

    def _content_cleanup(self, content: str) -> str:
        """This  function removes from downloaded content unwanted patterns - like ads, etc."""
        if self.patterns:
            for pattern in self.patterns.content_cleanup:
                if pattern.regex:
                    content = re.sub(pattern.regex, "", content)
        return content

    def _content_cleanup_xpath(self):
        if self.patterns:
            for pattern in self.patterns.content_cleanup:
                if pattern.xpath:
                    for bad in self.tree.xpath(pattern.xpath):
                        bad.getparent().remove(bad)

    def process(self) -> ArticleModel:
        self.html = self._content_cleanup(self.html)
        self.tree = fromstring(self.html)
        self._content_cleanup_xpath()
        # self.get_tags()
        return ArticleModel(
            url=self.url,
            title=self.get_title(),
            date=self.get_date(),
            images=self.get_images(),
            content=self.get_content(),
            comments=self.get_comments(),
        )
