#!/usr/bin/env python3
# -*- coding : utf-8 -*-

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

    def __init__(self, name, title, images=[], chapters=[]):
        self.name = name
        self.title = title
        self.images = images
        self.cover = Cover(name, title, images)
        self.chapters = chapters


    def addChapter(self, article, language):
        number = len(self.chapters) + 1
        self.chappters.append(Chapter(article, number, language))

    def create(self):
        self.book = epub.EpubBook()
        for chapter in self.chapters:
            self.book.add_item(chapter.epub)
            self.book.spine.append(chapter.epub)
            self.book.table_of_contents.append(chapter.epub)


class Chapter(object):

    def __init__(self, article, number, language):
        """
        :param article: Article class
        """
        self.epub = epub.EpubHtml(title=article.title, file_name='chap_' + str(number) + '.xhtml', lang=language)
        self.epub.content = '<h2>{}</h2>{}<p><i><a href="{}">{}</a></i></p>'.format(article.title, article.date,
                                                                                    article.url, article.url)

