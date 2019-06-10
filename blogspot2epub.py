#!/usr/bin/env python
# -*- coding: utf-8 -*-
# blogspot2epub
# version 0.2
# author: Bohdan Bobrowski bohdan@bobrowski.com.pl

import os
import re
import sys
import hashlib
from ebooklib import epub
from datetime import datetime
from lxml import html
from lxml import etree
from os import listdir
from os.path import isfile, join
from BeautifulSoup import BeautifulStoneSoup


def HTMLEntitiesToUnicode(text):
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text




# Generate file namespace
book_file_name = sys.argv[1] + '.blogspot.com'
book.set_title(get_cover_title(title, START_DATE, END_DATE))
try:
    start_date_obj = datetime.strptime(translate_month(START_DATE,BLOG_LANGUAGE), '%d %B %Y')
    end_date_obj = datetime.strptime(translate_month(END_DATE,BLOG_LANGUAGE), '%d %B %Y')
    if START_DATE == END_DATE:
        book_file_name = book_file_name + '_' + start_date_obj.strftime('%Y.%m.%d')
    else:
        book_file_name = book_file_name + '_' + end_date_obj.strftime('%Y.%m.%d') + '-' + start_date_obj.strftime('%Y.%m.%d')
except:
    pass

# Add cover - if file exist
book.spine.append('nav')
generate_cover(book_file_name, all_image_files)
book.set_cover(book_file_name + '.jpg', open(book_file_name + '.jpg', 'rb').read())
book.spine.append('cover')
book.spine.reverse()
# os.remove(book_file_name + '.jpg')

# Add table of contents
table_of_contents.reverse()
book.toc = table_of_contents

# Add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# Add css file
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

# Add images do epub file_name
if INCLUDE_IMAGES:
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

# Save damn ebook
epub.write_epub(book_file_name + '.epub', book, {})
fix_cover(book_file_name)
