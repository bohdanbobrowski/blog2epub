import datetime
import locale
import os
import re
import tempfile
import zipfile

from ebooklib.epub import (  # type: ignore
    EpubBook,
    EpubHtml,
    EpubItem,
    EpubNav,
    EpubNcx,
    write_epub,
)

from blog2epub.common.cover import Cover
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import ArticleModel, BookModel
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
        destination_folder: str = ".",
        platform_name: str = "",
    ):
        self.start: datetime.date | None = None
        self.end: datetime.date | None = None
        self.file_full_path: str | None = None
        self.cover: Cover | None = None
        self.cover_image_path: str | None = None
        self.book: EpubBook | None = None
        self.book_data = book_data
        self.url = book_data.url
        self.subtitle = None
        self.configuration = configuration
        self.interface = interface
        self._set_locale()
        self.chapters: list[Chapter] = []
        self.table_of_contents: list[EpubHtml] = []
        self.file_name: str = self._get_new_file_name()
        self.destination_folder = destination_folder
        self.platform_name = platform_name

    def _set_locale(self):
        try:
            locale.setlocale(locale.LC_ALL, self.configuration.language)
            self.interface.print(f"Locale set as {self.configuration.language}")
        except locale.Error:
            self.interface.print(f"Can't set locale as {self.configuration.language}, but nevermind.")

    def _get_subtitle(self):
        if self.end is None:
            return self.start.strftime("%d %B %Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.start.strftime("%d") + "-" + self.end.strftime("%d %B %Y")
        if self.start.strftime("%Y.%m") == self.end.strftime("%Y.%m"):
            return self.start.strftime("%d %B") + " - " + self.end.strftime("%d %B %Y")
        return self.start.strftime("%d %B %Y") + " - " + self.end.strftime("%d %B %Y")

    def _get_new_file_name(self) -> str:
        new_file_name = self.book_data.file_name_prefix
        if self.start:
            start_date: str = self.start.strftime("%Y.%m.%d")
            if self.end and self.start != self.end:
                end_date: str = self.end.strftime("%Y.%m.%d")
                new_file_name = f"{self.book_data.file_name_prefix}_{start_date}-{end_date}"
            else:
                new_file_name = f"{self.book_data.file_name_prefix}_{start_date}"
        return f"{new_file_name}.epub"

    def _add_chapters(self, articles: list[ArticleModel]):
        self.chapters = []
        for article in articles:
            number = len(self.chapters) + 1
            try:
                self.chapters.append(Chapter(article, number, self.configuration.language))
            except TypeError as e:
                print(e)

    def get_cover_title(self):
        cover_title = self.book_data.title + " "
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
        self.cover = Cover(
            dirs=self.book_data.dirs,
            interface=self.interface,
            file_name=self.file_name,
            blog_url=self.book_data.file_name_prefix,
            title=self.book_data.title,
            subtitle=self.subtitle,
            images=self.book_data.images,
            platform_name=self.platform_name,
            images_bw=self.configuration.images_bw,
            images_size=self.configuration.images_size,
        )
        cover_file_name, cover_file_full_path = self.cover.generate()
        self.cover_image_path = cover_file_full_path
        cover_html = self.cover_html.replace("###FILE###", cover_file_name)
        cover_html_fn = "EPUB/cover.xhtml"
        content_opf_fn = "EPUB/content.opf"
        if os.path.isfile(self.file_full_path):
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

            self.interface.print(f"Epub created: {self.file_full_path}")

    def _upgrade_opf(self, content_opt, cover_file_name):
        new_manifest = (
            '<manifest><item href="cover.xhtml" id="cover" media-type="application/xhtml+xml"/>'
            + f'<item href="{cover_file_name}" id="cover_img" media-type="image/jpeg"/>'
        )
        content_opt = content_opt.decode("utf-8").replace("<manifest>", new_manifest)
        return content_opt

    def _add_table_of_contents(self, ebook: EpubBook):
        self.table_of_contents.reverse()
        ebook.toc = self.table_of_contents
        ebook.add_item(EpubNcx())
        ebook.add_item(EpubNav())

    def _add_epub_css(self, ebook: EpubBook):
        nav_css = EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=self.style,
        )
        ebook.add_item(nav_css)

    def _include_images(self):
        images_included = set()
        if self.configuration.include_images:
            for image_number, image in enumerate(self.book_data.images, start=1):
                if (
                    image
                    and image.hash not in images_included
                    and os.path.isfile(os.path.join(self.book_data.dirs.images, image.file_name))
                ):
                    with open(os.path.join(self.book_data.dirs.images, image.file_name), "rb") as f:
                        image_content = f.read()
                    epub_img = EpubItem(
                        uid=f"img{image_number}",
                        file_name="images/" + image.file_name,
                        media_type="image/jpeg",
                        content=image_content,
                    )
                    self.book.add_item(epub_img)
                    images_included.add(image.hash)

    def _update_start_end_date(self, articles: list[ArticleModel]):
        self.start = self.end = None
        article_dates = []
        for article in articles:
            if article.date is not None:
                article_dates.append(article.date)
        if article_dates:
            article_dates.sort()
            self.start = article_dates[0]
            self.end = article_dates[-1]

    def _get_ebook(self) -> EpubBook:
        ebook = EpubBook()
        ebook.set_title(self.book_data.title)
        ebook.set_language(self.configuration.language)
        ebook.add_author(f"{self.book_data.title}, {self.book_data.file_name_prefix}")
        for chapter in self.chapters:
            ebook.add_item(chapter.epub)
            ebook.spine.append(chapter.epub)  # Important!
            self.table_of_contents.append(chapter.epub)
        self._add_table_of_contents(ebook)
        self._add_epub_css(ebook)
        ebook.spine.append("nav")
        ebook.spine.append("cover")
        ebook.spine.reverse()
        if self.book_data.description:
            ebook.add_metadata("DC", "description", "\n".join(self.book_data.description))
        return ebook

    def _get_file_full_path(self, destination_folder: str | None) -> str:
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
            file_full_path = file_full_path_name + "_[" + str(counter) + "]" + file_extension
            counter += 1
        return file_full_path

    def save(
        self,
        articles: list[ArticleModel] | None = None,
        destination_folder: str | None = None,
        file_name: str | None = None,
    ):
        if articles is None:
            articles = self.book_data.articles
        self._add_chapters(articles)
        self._update_start_end_date(articles)
        self.subtitle = self._get_subtitle()
        self.file_name = file_name or self._get_new_file_name()
        self.book = self._get_ebook()
        self._include_images()
        self.file_full_path = self._get_file_full_path(destination_folder)
        self.file_full_path = self._prevent_overwrite(self.file_full_path)
        write_epub(self.file_full_path, self.book, {})
        self._add_cover()


class Chapter:
    epub: EpubHtml | None = None

    def __init__(self, article: ArticleModel, number: int, language: str):
        uid = "chapter_" + str(number)
        self.epub: EpubHtml = EpubHtml(  # type: ignore
            title=article.title,
            uid=uid,
            file_name=uid + ".xhtml",
            lang=language,  # type: ignore
        )  # type: ignore
        tags = self._print_tags(article)
        art_date = "<p>"
        if article.date is not None:
            art_date += "<i>Created: " + article.date.strftime("%d %B %Y, %H:%M") + "</i><br/>"
        art_date += "<i>Accessed: " + article.accessed.strftime("%d %B %Y, %H:%M") + "</i>"
        art_date += "</p>"
        self.epub.content = (
            f"<h2>{article.title}</h2>{tags}{art_date}" + f'<p><i><a href="{article.url}">{article.url}</a></i></p>'
        )
        self.epub.content = f"<div>{self.epub.content}{article.content}{article.comments}</div>"

    def _print_tags(self, article):
        if not article.tags:
            return ""
        tags = []
        for tag in article.tags:
            tags.append('<span epub:type="keyword">' + tag + "<span>")
        tags = ", ".join(tags)
        return f"<h5>{tags}</h5>"
