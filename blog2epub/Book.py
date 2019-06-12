#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from datetime import datetime
import os

from ebooklib import epub
from blog2epub.Cover import Cover

class Book(object):
    """
    Book class used in Blogspot2Epub class.
    """

    style = '''
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
    '''

    def __init__(self, crawler):
        """
        :param crawler: instance of Crawler class
        """
        self.title = crawler.title
        self.description = crawler.description
        self.url = crawler.url
        self.dirs = crawler.dirs
        self.start = crawler.start
        self.end = crawler.end
        self.include_images = crawler.include_images
        self.images = crawler.images
        self.language = crawler.language
        self.chapters = []
        self.table_of_contents = []
        self.file_name_prefix = crawler.file_name
        self.update_file_name()
        self.destination_folder = crawler.destination_folder
        self.cover = None
        self.book = None
        self._add_chapters(crawler.articles)


    def update_file_name(self):
        file_name = self.file_name_prefix
        if self.start and self.end:
            start_date_obj = datetime.strptime(self._translate_month(self.start), '%d %B %Y')
            end_date_obj = datetime.strptime(self._translate_month(self.end), '%d %B %Y')
            if self.start == self.end:
                file_name = file_name  + '_' + start_date_obj.strftime('%Y.%m.%d')
            else:
                file_name = file_name + '_' + end_date_obj.strftime('%Y.%m.%d') + '-' + start_date_obj.strftime('%Y.%m.%d')
        self.file_name = file_name + ".epub"

    def _translate_month(self, date):
        if self.language == 'pl':
            date = date.replace('stycznia', 'january')
            date = date.replace('lutego', 'february')
            date = date.replace('marca', 'march')
            date = date.replace('kwietnia', 'april')
            date = date.replace('maja', 'may')
            date = date.replace('czerwca', 'june')
            date = date.replace('lipca', 'july')
            date = date.replace('sierpnia', 'august')
            date = date.replace('września', 'september')
            date = date.replace('października', 'october')
            date = date.replace('listopada', 'november')
            date = date.replace('grudnia', 'december')
        return date

    def _add_chapters(self, articles):
        for article in articles:
            number = len(self.chapters) + 1
            self.chapters.append(Chapter(article, number, self.language))

    def get_cover_title(self):
        cover_title = self.title + ' '
        if self.start == self.end:
            cover_title = cover_title + str(self.start)
        else:
            end_date = self.end.split(' ')
            start_date = start.split(' ')
            if len(end_date) == len(start_date):
                ed = []
                for i, d in enumerate(end_date):
                    if d != start_date[i]:
                        ed.append(d)
            ed = ' '.join(ed)
            cover_title = cover_title + ed + '-' + start
        return cover_title

    def _get_book_title(self):
        self.book.set_title(self.title, self.start, self.end)

    def _add_cover(self):
        self.book.spine.append('nav')
        # generate_cover(book_file_name, all_image_files)
        # book.set_cover(book_file_name + '.jpg', open(book_file_name + '.jpg', 'rb').read())
        # book.spine.append('cover')
        self.book.spine.reverse()
        # os.remove(book_file_name + '.jpg')

    def _add_table_of_contents(self):
        # TODO
        # Add table of contents
        self.table_of_contents.reverse()
        self.book.toc = self.table_of_contents
        # Add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

    def _add_epub_css(self):
        # Add css file
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=self.style)
        self.book.add_item(nav_css)

    def _include_images(self):
        # Add images do epub file_name
        if self.include_images:
            try:
                converted_images = [f for f in listdir(images_path) if isfile(join(images_path, f))]
            except NameError:
                converted_images = []
            for i, image in enumerate(converted_images):
                if image in images_included:
                    image_cont = None
                    with open(images_path + image, 'r') as content_file:
                        image_cont = content_file.read()
                    epub_img = epub.EpubItem(uid="img" + str(i), file_name="images/" + image, media_type="image/jpeg",
                                             content=image_cont)
                    book.add_item(epub_img)

    def save(self):
        self.update_file_name()
        self.book = epub.EpubBook()
        for chapter in self.chapters:
            self.book.add_item(chapter.epub)
            self.book.spine.append(chapter.epub)
            self.table_of_contents.append(chapter.epub)
        self._add_table_of_contents()
        self._add_epub_css()
        epub.write_epub(os.path.join(self.destination_folder, self.file_name), self.book, {})
        self.cover = Cover(self)
        self.cover.generate()
        self.book.set_cover(self.file_name + '.jpg', open(self.file_name + '.jpg', 'rb').read())
        self.cover.fix()

class Chapter(object):

    def __init__(self, article, number, language):
        """
        :param article: Article class
        """
        uid = 'chapter_' + str(number)
        self.epub = epub.EpubHtml(title=article.title, uid=uid, file_name=uid + '.xhtml', lang=language)
        self.epub.content = '<h2>{}</h2>{}<p><i><a href="{}">{}</a></i></p>'.format(article.title, article.date,
                                                                                    article.url, article.url)
        self.epub.content = self.epub.content + article.content + article.comments

