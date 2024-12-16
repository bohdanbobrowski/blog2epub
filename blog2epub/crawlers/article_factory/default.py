import html
import re
from datetime import datetime

import dateutil
import pytz
from lxml.etree import tostring
from lxml.html.soupparser import fromstring
from strip_tags import strip_tags  # type: ignore

from blog2epub.common.language_tools import translate_month
from blog2epub.crawlers.article_factory.abstract import AbstractArticleFactory
from blog2epub.models.book import ArticleModel, ImageModel


class DefaultArticleFactory(AbstractArticleFactory):
    def get_title(self) -> str | None:
        title = None
        if self.tree is not None and self.patterns is not None:
            for title_pattern in self.patterns.title:
                if title_pattern.xpath is not None:
                    title = self.tree.xpath(title_pattern.xpath)
                    if isinstance(title, list) and len(title) > 0:
                        title = title[0]
                    if len(title) > 1:
                        break
            if title is None:
                for title_pattern in self.patterns.title:
                    if title_pattern.regex is not None:
                        title_result = re.search(title_pattern.regex, self.html.decode())
                        if title_result is not None:
                            title = title_result.group(1).strip()
                            if len(title) > 1:
                                break
        while isinstance(title, list):
            try:
                title = title[0]
            except IndexError:
                title = None
        if title is not None and len(title) > 1:
            title = html.unescape(title.strip())
        return title

    def get_date(self) -> datetime | None:
        result_date = None
        if self.patterns is not None:
            for date_pattern in self.patterns.date:
                if date_pattern.regex:
                    date_match = re.findall(date_pattern.regex, self.html.decode("utf-8"))
                    if date_match:
                        result_date = f"{date_match[0][0]} {date_match[0][1]} {date_match[0][2]}"
                        break
                    pass
                elif date_pattern.xpath:
                    date = self.tree.xpath(date_pattern.xpath)
                    if len(date) > 0:
                        result_date = date[0]
                        break
        if result_date is None:
            d = self.url.split("/")
            if len(d) > 4:
                result_date = f"{d[3]}-{d[4]}-01 00:00"
            else:
                result_date = str(datetime.now())
        else:
            result_date = translate_month(result_date, self.language)  # type: ignore
        try:
            result_datetime_obj = dateutil.parser.parse(result_date)  # type: ignore
            try:
                return pytz.UTC.localize(result_datetime_obj)
            except ValueError:
                pass
            return result_datetime_obj
        except (IndexError, dateutil.parser.ParserError):  # type: ignore
            pass
        return None

    def _remove_images(self, images_html: list[bytes], images_list: list[ImageModel]):
        if len(images_html) > 0 and len(images_list) == len(images_html):
            self.html: bytes = tostring(self.tree)
            for key, img_obj in enumerate(images_list):
                replace_pattern = f"#blog2epubimage#{img_obj.hash}#".encode()
                image_html = images_html[key]
                self.html = self.html.replace(image_html, replace_pattern)
            self.tree = fromstring(self.html)

    def get_images(self) -> list[ImageModel]:
        self.images_list = []
        images_html: list[bytes] = []
        self.interface.print("Downloading", end="")
        if self.patterns is not None:
            for pattern in self.patterns.images:
                if pattern.regex:
                    pass
                elif pattern.xpath:
                    images_in_pattern = self.tree.xpath(pattern.xpath)
                    for image_element in images_in_pattern:
                        try:
                            image_url = image_element.xpath("@src")[0]
                        except IndexError:
                            break
                        try:
                            image_description = image_element.xpath("@alt")[0]
                        except IndexError:
                            image_description = ""
                        image_obj = ImageModel(url=image_url, description=image_description)
                        if self.download_callback:
                            if self.download_callback():
                                break
                        if self.downloader.download_image(image_obj):
                            self.images_list.append(image_obj)
                            self.interface.print(".", end="")
                            images_html.append(tostring(image_element))
            self._remove_images(images_html=images_html, images_list=self.images_list)
            # images will be inserted back after cleaning the content
        self.interface.delete_line()
        self.interface.print("")
        return self.images_list

    def _insert_images(self, article_content: str, images_list: list[ImageModel]) -> str:
        for image in images_list:
            image_html = (
                '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" '
                + 'style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF;'
                'box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody>'
            )
            image_html += (
                f'<tr><td style="text-align: center;"><img border="0" src="images/{image.file_name}" /></td></tr>'
            )
            if image.description:
                image_html += f'<tr><td class="tr-caption" style="text-align: center;">{image.description}</td></tr>'
            image_html += "</tbody></table>"
            article_content = article_content.replace(f"#blog2epubimage#{image.hash}#", image_html)
        return article_content

    def get_content(self) -> str:
        content = ""
        if self.patterns:
            for pattern in self.patterns.content:
                if pattern.xpath:
                    content_element = self.tree.xpath(pattern.xpath)
                    if content_element:
                        content_html = tostring(content_element[0]).decode("utf8")
                        content_html = self._content_cleanup(content_html)
                        content_html = self._content_cleanup_xpath(content_html)
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
                                "pre",
                            ],
                        )
                        content = re.sub(r"</i>[\s]*<i>", "", content)
                        content = re.sub(r"</b>[\s]*<b>", "", content)
                if content:
                    content = self._insert_images(content, self.images_list)
                    return content
        return content

    def get_tags(self) -> list[str]:
        tags = self.tree.xpath('//a[@rel="tag"]//text()')
        output = []
        for t in tags:
            t = t.strip()
            output.append(t)
        return output

    def get_comments(self) -> str:
        headers = self.tree.xpath('//div[@id="comments"]/h4/text()')
        result_comments = ""
        if len(headers) == 1:
            result_comments = "<hr/><h3>" + headers[0] + "</h3>"
        comments_in_article = self.tree.xpath('//div[@class="comment-block"]//text()')
        if comments_in_article:
            tag = "h4"
            for c in comments_in_article:
                c = c.strip()
                if c not in ("Odpowiedz", "Usuń"):
                    result_comments += "<" + tag + ">" + c + "</" + tag + ">"
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
                    result_comments += f"<h4>{a}</h4>"
                    result_comments += f"<p>{c}</p>"
            except IndexError:
                pass
        return result_comments

    def _content_cleanup(self, content: str | bytes) -> str:
        """This  function removes from downloaded content unwanted patterns - like ads, etc."""
        if isinstance(content, bytes):
            content = content.decode("utf8")
        if self.patterns:
            for pattern in self.patterns.content_cleanup:
                if pattern.regex:
                    content = re.sub(pattern.regex, "", content)
                if pattern.xpath:
                    for bad in self.tree.xpath(pattern.xpath):
                        bad.getparent().remove(bad)
        return content

    def _content_cleanup_xpath(self, input_content: str | bytes) -> str:
        """This  function removes from downloaded content unwanted patterns - but using xpath"""
        xpath_patterns = []
        if self.patterns:
            for pattern in self.patterns.content_cleanup:
                if pattern.xpath:
                    xpath_patterns.append(pattern)
        if xpath_patterns:
            if isinstance(input_content, str):
                content_tree = fromstring(input_content.encode())
            else:
                content_tree = fromstring(input_content)
            if self.patterns:
                for pattern in self.patterns.content_cleanup:
                    if pattern.xpath:
                        for bad in content_tree.xpath(pattern.xpath):
                            bad.getparent().remove(bad)
            return tostring(content_tree).decode()
        if isinstance(input_content, bytes):
            return input_content.decode()
        else:
            return input_content

    def process(self) -> ArticleModel | None:
        try:
            self.tree = fromstring(self.html)
            return ArticleModel(
                url=self.url,
                title=self.get_title(),
                date=self.get_date(),
                images=self.get_images(),
                tags=self.get_tags(),
                content=self.get_content(),
                comments=self.get_comments(),
            )
        except ValueError:
            self.interface.print(f"Contents of: {self.url} can not be parsed. Skipping!")
            return None
