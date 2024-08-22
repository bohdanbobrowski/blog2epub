import datetime
import locale
import os
import re
import tempfile
import zipfile
from typing import Optional, List

from ebooklib import epub  # type: ignore

from blog2epub.common.cover import Cover
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import BookModel, DirModel, ArticleModel
from blog2epub.models.configuration import ConfigurationModel


class Book:
    """Book class used in blog2epub class."""

    style = """
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
    }
    h2 {
         text-align: left;
         text-transform: uppercase;
         font-weight: 200;     
    }
    ol {
            list-style-type: none;
    }
    ol > li:first-child {
            margin-top: 0.3em;
    }
    nav[epub|type~='toc'] > ol > li > ol  {
        list-style-type:square;
    }
    nav[epub|type~='toc'] > ol > li > ol > li {
            margin-top: 0.3em;
    }
    """

    cover_html = """<?xml version='1.0' encoding='utf-8'?>
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
    <meta name="calibre:cover" content="true"/>
    <title>Cover</title>
    <style type="text/css" title="override_css">
    @page {
        padding: 0pt;
        margin: 0pt;
    }
    body {
        text-align: center;
        padding: 0pt;
        margin: 0pt;
    }
    </style>
    </head>
    <body>
    <div><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="100%" height="100%" viewBox="0 0 600 800" preserveAspectRatio="none">
    <image id="cover_img" width="600" height="800" xlink:href="###FILE###"/>
    </svg></div>
    </body>
    </html>"""

    def __init__(
        self,
        book_data: BookModel,
        configuration: ConfigurationModel,
        interface: EmptyInterface,
        destination_folder: str,
    ):
        self.title = book_data.title
        self.description = book_data.description
        self.url = book_data.url
        self.dirs: DirModel = book_data.dirs
        self.start: Optional[datetime.date]
        self.end: Optional[datetime.date]
        self.subtitle = None
        self.images = book_data.images
        self.configuration = configuration
        self.interface = interface
        self._set_locale()
        self.chapters: List[Chapter] = []
        self.table_of_contents: List[epub.EpubHtml] = []
        self.file_name: str = self._get_new_file_name()
        self.file_name_prefix = book_data.file_name_prefix
        self.file_full_path: Optional[str] = None
        self.destination_folder = destination_folder
        self.cover = None
        self.cover_image_path = None
        self.book = None

    def _set_locale(self):
        try:
            locale.setlocale(locale.LC_ALL, self.configuration.language)
            self.interface.print(f"Locale set as {self.configuration.language}")
        except locale.Error:
            self.interface.print(
                f"Can't set locale as {self.configuration.language}, but nevermind."
            )

    def _get_subtitle(self):
        if self.end is None:
            return self.start.strftime("%d %B %Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.start.strftime("%d") + "-" + self.end.strftime("%d %B %Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.start.strftime("%d %B") + " - " + self.end.strftime("%d %B %Y")
        return self.start.strftime("%d %B %Y") + " - " + self.end.strftime("%d %B %Y")

    def _get_new_file_name(self) -> str:
        new_file_name = self.file_name_prefix
        if self.start:
            start_date: str = self.start.strftime("%Y.%m.%d")
            if self.end and self.start != self.end:
                end_date: str = self.end.strftime("%Y.%m.%d")
                new_file_name = f"{self.file_name_prefix}_{start_date}-{end_date}"
            else:
                new_file_name = f"{self.file_name_prefix}_{start_date}"
        return f"{new_file_name}.epub"

    def _add_chapters(self, articles: List[ArticleModel]):
        self.chapters = []
        for article in articles:
            number = len(self.chapters) + 1
            if article.content:
                try:
                    self.chapters.append(
                        Chapter(article, number, self.configuration.language)
                    )
                except TypeError as e:
                    print(e)
            else:
                self.interface.print(
                    f"Skipping article: {number}. {str(article.title)}"
                )

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

    def _add_cover(self):
        self.cover = Cover(self)
        cover_file_name, cover_file_full_path = self.cover.generate()
        self.cover_image_path = os.path.join(cover_file_name, cover_file_full_path)
        cover_html = self.cover_html.replace("###FILE###", cover_file_name)
        cover_html_fn = "EPUB/cover.xhtml"
        content_opf_fn = "EPUB/content.opf"
        with zipfile.ZipFile(self.file_full_path, "r") as zf:
            content_opf = zf.read(content_opf_fn)
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self.file_full_path))
        os.close(tmpfd)
        with zipfile.ZipFile(self.file_full_path, "r") as zin:
            with zipfile.ZipFile(tmpname, "w") as zout:
                zout.comment = zin.comment  # preserve the comment
                for item in zin.infolist():
                    if item.filename not in [cover_html_fn, content_opf_fn]:
                        zout.writestr(item, zin.read(item.filename))
        os.remove(self.file_full_path)
        os.rename(tmpname, self.file_full_path)
        with zipfile.ZipFile(self.file_full_path, "a") as zf:
            zf.writestr(cover_html_fn, cover_html)
            zf.write(cover_file_full_path, "EPUB/" + cover_file_name)
            zf.writestr(content_opf_fn, self._upgrade_opf(content_opf, cover_file_name))
        if os.path.isfile(self.file_full_path):
            if hasattr(self.interface, "notify"):
                self.interface.notify(
                    "blog2epub",
                    "Epub created",
                    self.file_full_path,
                    cover_file_full_path,
                )
            self.interface.print(f"Epub created: {self.file_full_path}")

    def _upgrade_opf(self, content_opt, cover_file_name):
        new_manifest = (
            '<manifest><item href="cover.xhtml" id="cover" media-type="application/xhtml+xml"/>'
            + f'<item href="{cover_file_name}" id="cover_img" media-type="image/jpeg"/>'
        )
        content_opt = content_opt.decode("utf-8").replace("<manifest>", new_manifest)
        return content_opt

    def _add_table_of_contents(self, ebook: epub.EpubBook):
        self.table_of_contents.reverse()
        ebook.toc = self.table_of_contents
        ebook.add_item(epub.EpubNcx())
        ebook.add_item(epub.EpubNav())

    def _add_epub_css(self, ebook: epub.EpubBook):
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=self.style,
        )
        ebook.add_item(nav_css)

    def _include_images(self):
        images_included = []
        if self.configuration.include_images:
            for i, image in enumerate(self.images, start=1):
                if (
                    image
                    and image not in images_included
                    and os.path.isfile(os.path.join(self.dirs.images, image.hash))
                ):
                    with open(os.path.join(self.dirs.images, image.hash), "rb") as f:
                        image_content = f.read()
                    epub_img = epub.EpubItem(
                        uid="img%s" % i,
                        file_name="images/" + image.hash,
                        media_type="image/jpeg",
                        content=image_content,
                    )
                    self.book.add_item(epub_img)
                    images_included.append(image)

    def _update_start_end_date(self, articles: List[ArticleModel]):
        self.start = self.end = None
        article_dates = []
        for article in articles:
            article_dates.append(article.date)
        article_dates.sort()
        self.start = article_dates[0]
        self.end = article_dates[-1]

    def _get_ebook(self) -> epub.EpubBook:
        ebook = epub.EpubBook()
        ebook.set_title(self.title)
        ebook.set_language(self.configuration.language)
        ebook.add_author(f"{self.title}, {self.file_name_prefix}")
        for chapter in self.chapters:
            ebook.add_item(chapter.epub)
            ebook.spine.append(chapter.epub)  # Important!
            self.table_of_contents.append(chapter.epub)
        self._add_table_of_contents(ebook)
        self._add_epub_css(ebook)
        ebook.spine.append("nav")
        ebook.spine.append("cover")
        ebook.spine.reverse()
        if self.description:
            ebook.add_metadata("DC", "description", "\n".join(self.description))
        return ebook

    def _get_file_full_path(self, destination_folder: Optional[str]) -> str:
        if destination_folder is None:
            return os.path.join(self.destination_folder, self.file_name)
        else:
            return os.path.join(destination_folder, self.file_name)

    @staticmethod
    def _prevent_overwrite(file_full_path: str) -> str:
        """This function prevents overwriting existing file."""
        file_full_path_name, file_extension = os.path.splitext(file_full_path)
        file_full_path_name = re.sub(r"_\[[0-9]+\]$", "", file_full_path_name)
        counter = 1
        while os.path.exists(file_full_path):
            file_full_path = (
                file_full_path_name + "_[" + str(counter) + "]" + file_extension
            )
            counter += 1
        return file_full_path

    def save(
        self,
        articles: List[ArticleModel],
        destination_folder: Optional[str] = None,
        file_name: Optional[str] = None,
    ):
        self._add_chapters(articles)
        self._update_start_end_date(articles)
        self.subtitle = self._get_subtitle()
        self.file_name = file_name or self._get_new_file_name()
        self.book = self._get_ebook()
        self._include_images()
        self.file_full_path = self._get_file_full_path(destination_folder)
        self.file_full_path = self._prevent_overwrite(self.file_full_path)
        epub.write_epub(self.file_full_path, self.book, {})
        self._add_cover()


class Chapter:
    epub: Optional[epub.EpubHtml] = None

    def __init__(self, article, number, language):
        """
        :param article: Article class
        """
        uid = "chapter_" + str(number)
        self.epub: epub.EpubHtml = epub.EpubHtml(
            title=article.title, uid=uid, file_name=uid + ".xhtml", lang=language
        )
        tags = self._print_tags(article)
        art_date = article.date.strftime("%d %B %Y, %H:%M")
        self.epub.content = (
            f"<h2>{article.title}</h2>{tags}{art_date}"
            + f'<p><i><a href="{article.url}">{article.url}</a></i></p>'
        )
        self.epub.content = (
            "<div>" + self.epub.content + article.content + article.comments + "</div>"
        )

    def _print_tags(self, article):
        if not article.tags:
            return ""
        tags = []
        for tag in article.tags:
            tags.append('<span epub:type="keyword">' + tag + "<span>")
        tags = ", ".join(tags)
        return f"<h5>{tags}</h5>"
