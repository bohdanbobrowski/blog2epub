#!/usr/bin/env python
# -*- coding: utf-8 -*-
# blogspot2epub
# version 0.2
# author: Bohdan Bobrowski bohdan@bobrowski.com.pl

import os
import zipfile
import tempfile
import json
import re
import sys
import pycurl
import urllib2
import hashlib
from ebooklib import epub
from datetime import datetime
from random import shuffle
from slugify import slugify
from lxml import html
from lxml import etree
import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from os import listdir
from os.path import isfile, join
from BeautifulSoup import BeautifulStoneSoup


class WWWDownloader:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf


def download_web_page(url, forceDownload = False):
    m = hashlib.md5()
    m.update(url)
    url_hash = m.hexdigest()
    html_path = './' + sys.argv[1] + '/html/'
    if not os.path.exists(html_path):
        os.makedirs(html_path)
    html_file_path = html_path + url_hash + '.html'
    if forceDownload or not os.path.isfile(html_file_path):
        try:
            www = WWWDownloader()
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEFUNCTION, www.body_callback)
            c.setopt(c.HEADER, 1);
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.COOKIEFILE, '')
            c.setopt(c.CONNECTTIMEOUT, 30)
            c.setopt(c.TIMEOUT, 30)
            c.setopt(c.COOKIEFILE, '')
            c.perform()
        except Exception, err:
            print "- Connection error."
            print err
            exit()
        else:
            www_html = www.contents
            html_file = open(html_file_path, "w+")
            html_file.write(www_html)
            html_file.close()
    else:
        with open(html_file_path, 'r') as html_file:
            www_html = html_file.read()
    return www_html


def get_images(html):
    images = []
    return images


def get_date(str_date):
    return unicode(re.sub('[^\,]*, ', '', str_date))


def make_thumb(img, size):
    cropped_img = crop_image(img, size)
    cropped_img.thumbnail(size, Image.ANTIALIAS)
    return cropped_img


def box_params_center(width, height):
    if is_landscape(width, height):
        upper_x = int((width / 2) - (height / 2))
        upper_y = 0
        lower_x = int((width / 2) + (height / 2))
        lower_y = height
        return upper_x, upper_y, lower_x, lower_y
    else:
        upper_x = 0
        upper_y = int((height / 2) - (width / 2))
        lower_x = width
        lower_y = int((height / 2) + (width / 2))
        return upper_x, upper_y, lower_x, lower_y


def is_landscape(width, height):
    if width >= height:
        return True
    else:
        return False


def crop_image(img, size):
    upper_x, upper_y, lower_x, lower_y = box_params_center(img.size[0], img.size[1])
    box = (upper_x, upper_y, lower_x, lower_y)
    region = img.crop(box)
    return region


def download_image(picture_url, original_picture, target_picture):    
    result = False
    if picture_url.startswith("//"):
        picture_url = "http:" + picture_url
    if not os.path.isfile(original_picture):
        try:
            u = urllib2.urlopen(picture_url)
            f = open(original_picture, 'wb')
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                f.write(buffer)
            f.close()
        except Exception as e:
            print e
    if INCLUDE_IMAGES and not os.path.isfile(target_picture) and os.path.isfile(original_picture):
        try:
            picture = Image.open(original_picture)
            if picture.size[0] > IMAGES_WIDTH or picture.size[1] > IMAGES_HEIGHT:
                picture.thumbnail([IMAGES_WIDTH, IMAGES_HEIGHT], Image.ANTIALIAS)
            picture = picture.convert('L')
            picture.save(target_picture, format='JPEG', quality=IMAGES_QUALITY)
        except Exception as e:
            print e
    if os.path.isfile(target_picture):
        result = True
    return result

def get_cover_title(cover_title, start, end):
    cover_title = cover_title + ' '
    if start == end:
        cover_title = cover_title + str(start)
    else:
        end_date = end.split(' ')
        start_date = start.split(' ')
        if len(end_date) == len(start_date):
            ed = []
            for i, d in enumerate(end_date):
                if d != start_date[i]:
                    ed.append(d)
        ed = ' '.join(ed)
        cover_title = cover_title + ed + '-' + start
    return cover_title


def generate_cover(file_name, images_list):
    tile_size = 120
    tiles_count_y = 5
    tiles_count_x = 7
    cover_image = Image.new('RGB', (600, 800))
    cover_draw = ImageDraw.Draw(cover_image)
    dark_factor = 1
    if len(images_list) > 0:        
        shuffle(images_list)
        i = 1
        for x in range(0, tiles_count_x):
            for y in range(0, tiles_count_y):
                try:
                    thumb = make_thumb(Image.open(images_list[i - 1]), (tile_size, tile_size))
                    thumb = thumb.point(lambda p: p * dark_factor)
                    dark_factor = dark_factor - 0.03
                    cover_image.paste(thumb, (y * tile_size, x * tile_size))
                    i = i + 1
                except Exception as e:
                    print e
                if i > len(images_list):
                    i = 1
    cover_draw.text((15, 635), title, (255, 255, 255), font=ImageFont.truetype("Lato-Bold.ttf", 30))
    cover_draw.text((15, 760), sys.argv[1] + ".blogspot.com", (255, 255, 255),
                    font=ImageFont.truetype("Lato-Regular.ttf", 20))
    if START_DATE == END_DATE:
        cover_draw.text((15, 670), START_DATE, (150, 150, 150), font=ImageFont.truetype("Lato-Italic.ttf", 20))
    else:
        end_date = END_DATE.split(' ')
        start_date = START_DATE.split(' ')
        if len(end_date) == len(start_date):
            ed = []
            for i, d in enumerate(end_date):
                if d != start_date[i]:
                    ed.append(d)
        ed = ' '.join(ed)
        cover_draw.text((15, 670), ed + " - " + START_DATE, (150, 150, 150),
                        font=ImageFont.truetype("Lato-Italic.ttf", 20))
    cover_image = cover_image.convert('L')
    cover_image.save(file_name + '.jpg', format='JPEG', quality=100)


def get_blog_language(html, default_language):
    language = default_language;
    if re.search("'lang':[\s]*'([a-z^']+)'", html):
        language = re.search("'lang':[\s]*'([a-z^']+)'", html).group(1).strip().decode('utf-8')
    if re.search('lang="([a-z^"]+)"', html):
        language = re.search('lang="([a-z^"]+)"', html).group(1).strip().decode('utf-8')
    for arg in sys.argv:
        if arg.find('-ln=') == 0:
            language = arg.replace('-ln=', '')
        if arg.find('--language=') == 0:
            language = arg.replace('--language=', '')
    return language


def fix_cover(zipname):
    filename = 'EPUB/cover.xhtml'
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname+'.epub'))
    os.close(tmpfd)
    with zipfile.ZipFile(zipname+'.epub', 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment # preserve the comment
            for item in zin.infolist():
                if item.filename == filename:
                    cover_html = zin.read(filename)
                else:
                    zout.writestr(item, zin.read(item.filename))                
    os.remove(zipname+'.epub')
    os.rename(tmpname, zipname+'.epub')
    zf = zipfile.ZipFile(zipname+'.epub', 'r')
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
<image width="600" height="800" xlink:href="###FILE###"/>
</svg></div>
</body>
</html>"""
    cover_html = cover_html.replace('###FILE###',zipname+'.jpg')
    with zipfile.ZipFile(zipname+'.epub', mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, cover_html)

def HTMLEntitiesToUnicode(text):
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text

# Default params:
INCLUDE_IMAGES = True
IMAGES_QUALITY = 40
IMAGES_HEIGHT = 800
IMAGES_WIDTH = 600
LIMIT = False
SKIP = False
BLOG_LANGUAGE = 'en'

# Check CLI params
if len(sys.argv) < 2:
    print "usage: blogspot2epub <blog_name> [params...]"
    exit();

# Read CLI params
if '-n' in sys.argv or '--no-images' in sys.argv:
    INCLUDE_IMAGES = False

for arg in sys.argv:
    if arg.find('-l=') == 0:
        LIMIT = int(arg.replace('-l=', ''))
    if arg.find('--limit=') == 0:
        LIMIT = int(arg.replace('--limit=', ''))
    if arg.find('-s=') == 0:
        SKIP = int(arg.replace('-s=', ''))
    if arg.find('--skip=') == 0:
        SKIP = int(arg.replace('--skip=', ''))
    if arg.find('-q=') == 0:
        IMAGES_QUALITY = int(arg.replace('-q=', ''))
    if arg.find('--quality=') == 0:
        IMAGES_QUALITY = int(arg.replace('--quality=', ''))

START_DATE = False;
END_DATE = False;

book = epub.EpubBook()
table_of_contents = []
y = x = 1
BLOG_URL = 'http://' + sys.argv[1] + '.blogspot.com/'
images_included = []
all_image_files = []
while BLOG_URL != '':
    www_html = download_web_page(BLOG_URL, True)
    artykuly = re.findall(
        "<h3 class='post-title entry-title' itemprop='name'>[\s]*<a href='([^']*)'>([^>^<]*)</a>[\s]*</h3>", www_html)
    if x == 1:
        BLOG_LANGUAGE = get_blog_language(www_html, BLOG_LANGUAGE)
        title = re.search("<title>([^>^<]*)</title>", www_html).group(1).strip().decode('utf-8')
        book.set_language(BLOG_LANGUAGE)
        book.add_author(title + ', ' + sys.argv[1] + '.blogspot.com')
    BLOG_URL = ''
    if re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'", www_html):
        BLOG_URL = re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'",
                             www_html).group(1)
    for art in artykuly:
        if SKIP == False or y > SKIP:
            art_title = unicode(art[1].strip().decode('utf-8'))
            art_title = HTMLEntitiesToUnicode(art_title)
            print str(x) + '. ' + art_title
            art_html = download_web_page(art[0])
            art_tree = html.fromstring(art_html)
            art_date = art_tree.xpath('//h2[@class="date-header"]/span/text()')
            if START_DATE == False:
                START_DATE = get_date(art_date[0])
            END_DATE = get_date(art_date[0])
            if len(art_date) == 1:
                art_date = '<p><strong>' + art_date[0] + '</strong></p>'
            art_comments_h = art_tree.xpath('//div[@id="comments"]/h4/text()')
            art_comments = ''
            if len(art_comments_h) == 1:
                art_comments = '<hr/><h4>' + art_comments_h[0] + '</h4>'
            art_comments_c = art_tree.xpath('//div[@class="comment-block"]//text()')
            tag = u'h3';
            for acc in art_comments_c:
                acc = acc.strip()
                if acc != u'Odpowiedz' and acc != u'Usuń':
                    art_comments = art_comments + u'<' + tag + u'>' + acc + u'</' + tag + u'>'
                    if tag == u'h3': tag = u'p'
                if acc == u'Usuń': tag = u'h3'
            c = epub.EpubHtml(title=art_title, file_name='chap_' + str(x) + '.xhtml', lang='pl')
            # Post title:
            c.content = u'<h2>' + art_title + u'</h2>' + art_date + u'<p><i>' + art[0] + u'</i></p>'
            # Images:
            image_files = []
            images = re.findall(
                '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)',
                art_html)
            if len(images) > 0:
                for image in images:
                    image_url = image[0]
                    originals_path = "./" + sys.argv[1] + "/originals/"
                    if not os.path.exists(originals_path):
                        os.makedirs(originals_path)
                    images_path = "./" + sys.argv[1] + "/images/"
                    if not os.path.exists(images_path):
                        os.makedirs(images_path)
                    m = hashlib.md5()
                    m.update(image_url)
                    image_hash = m.hexdigest()
                    images_included.append(image_hash + ".jpg")
                    image_file_name = originals_path + image_hash + ".jpg"
                    image_file_name_dest = images_path + image_hash + ".jpg"
                    image_regex = '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="' + image[
                        0] + '"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">[^<]*</td></tr>[\s]*</tbody></table>'
                    try:
                        art_html = re.sub(image_regex, ' #blogspot2epubimage#' + image_hash + '# ', art_html)
                    except Exception as e:
                        print e
                    if download_image(image[0], image_file_name, image_file_name_dest):
                        image_files.append(image_file_name)
            art_tree = html.fromstring(art_html)
            images_nocaption = art_tree.xpath('//a[@imageanchor="1"]')
            if len(images_nocaption) > 0:
                for image in images_nocaption:
                    image = etree.tostring(image)
                    image_href = re.findall('href="([^"]*)"', image)
                    image_src = re.findall('src="([^"]*)"', image)
                    if INCLUDE_IMAGES:
                        originals_path = "./" + sys.argv[1] + "/originals/"
                        if not os.path.exists(originals_path):
                            os.makedirs(originals_path)
                        images_path = "./" + sys.argv[1] + "/images/"
                        if not os.path.exists(images_path):
                            os.makedirs(images_path)
                        image_url = '';
                        if len(image_href) > 0:
                            image_url = image_href[0]
                            image_regex = '<a href="' + image_url + '"[^>]*><img[^>]*></a>'
                        if len(image_src) > 0:
                            image_url = image_src[0]
                            image_regex = '<img[?=\sa-z\"0-9]*src="' + image_url + '"[^>]+>'
                        if len(image_url) > 0:
                            m = hashlib.md5()
                            m.update(image_url)
                            image_hash = m.hexdigest()
                            images_included.append(image_hash + ".jpg")
                            try:
                                art_html = re.sub(image_regex, ' #blogspot2epubimage#' + image_hash + '# ', art_html)
                                image_file_name = originals_path + image_hash + ".jpg"
                                image_file_name_dest = images_path + image_hash + ".jpg"
                                if download_image(image_url, image_file_name, image_file_name_dest):
                                    image_files.append(image_file_name)
                            except Exception, err:
                                print "Error:",err
                                # TODO: "sre_constants.error: multiple repeat" - try to handle this error
                    else:
                        art_html = art_html.replace(image, '')
            # Post content:
            art_tree = html.fromstring(art_html)
            art_content = art_tree.xpath("//div[contains(concat(' ',normalize-space(@class),' '),'post-body')]")
            if len(art_content) == 1:
                art_content = etree.tostring(art_content[0], pretty_print=True)
                art_content = re.sub('style="[^"]*"', '', art_content)
                art_content = re.sub('class="[^"]*"', '', art_content)
                images_md5 = re.findall('#blogspot2epubimage#([^#]*)', art_content)
                for image_md5 in images_md5:
                    for image in images:
                        m = hashlib.md5()
                        m.update(image[0])
                        image_caption = image[1].strip().decode('utf-8')
                        if m.hexdigest() == image_md5:
                            image_html = '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/' + image_md5 + '.jpg" /></td></tr><tr><td class="tr-caption" style="text-align: center;">' + image_caption + '</td></tr></tbody></table>'
                            art_content = art_content.replace('#blogspot2epubimage#' + image_md5 + '#', image_html)
                    for image in images_nocaption:
                        image = etree.tostring(image)
                        image_href = re.findall('href="([^"]*)"', image)
                        image_src = re.findall('src="([^"]*)"', image)
                        image_url = ''
                        if len(image_href) > 0:
                            image_url = image_href[0]
                        if len(image_src) > 0:
                            image_url = image_src[0]
                        if len(image_url) > 0:
                            m = hashlib.md5()
                            m.update(image_url)
                            if m.hexdigest() == image_md5:
                                image_html = '<img border="0" src="images/' + image_md5 + '.jpg" />'
                                art_content = art_content.replace('#blogspot2epubimage#' + image_md5 + '#', image_html)
                        else:
                            art_content = art_content.replace('#blogspot2epubimage#' + image_md5 + '#',
                                                              '<em>Image not found<em>')
                c.content = c.content + art_content
            c.content = c.content + art_comments
            book.add_item(c)
            book.spine.append(c)
            table_of_contents.append(c)
            x = x + 1
            if not LIMIT == False and x > LIMIT:
                BLOG_URL = ''
                break
            all_image_files = image_files + all_image_files
        y = y + 1


def translate_month(date, language):
    if language == 'pl':
        date = date.replace('stycznia','january');
        date = date.replace('lutego','february');
        date = date.replace('marca','march');
        date = date.replace('kwietnia','april');
        date = date.replace('maja','may');
        date = date.replace('czerwca','june');
        date = date.replace('lipca','july');
        date = date.replace('sierpnia','august');
        date = date.replace(u'września','september');
        date = date.replace(u'października','october');
        date = date.replace('listopada','november');
        date = date.replace('grudnia','december');
    return date


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

# Define CSS style
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
