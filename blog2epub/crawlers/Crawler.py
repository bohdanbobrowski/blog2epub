#!/usr/bin/env python3
# -*- coding : utf-8 -*-

import hashlib
import xml.etree.ElementTree as ET
import os
import re
import sys
from urllib.request import urlopen
from lxml.html.soupparser import fromstring
from PIL import Image

from blog2epub.Book import Book


def translate_month(date, language):
    if language == 'pl':
        date = date.replace('stycznia','january')
        date = date.replace('lutego','february')
        date = date.replace('marca','march')
        date = date.replace('kwietnia','april')
        date = date.replace('maja','may')
        date = date.replace('czerwca','june')
        date = date.replace('lipca','july')
        date = date.replace('sierpnia','august')
        date = date.replace('września','september')
        date = date.replace('października','october')
        date = date.replace('listopada','november')
        date = date.replace('grudnia','december')
    return date


class Crawler(object):
    """
    Universal blog crawler.
    """

    def __init__(self, url, include_images=True, images_height=800, images_width=600, images_quality=40, start=None,
                 end=None, limit=False, skip=False, force_download=False, interface=None):

        self.url = self._prepare_url(url)
        self.url_to_crawl = self._prepare_url_to_crawl(self.url)
        self.name = self._prepare_name(self.url)

        self.include_images = include_images
        self.images_quality = images_quality
        self.images_height = images_height
        self.images_width = images_width
        self.start = start
        self.end = end
        self.limit = limit
        self.skip = skip
        self.force_download = force_download
        self.interface = self._get_the_interface(interface)
        self.dirs = Dirs(self.url)
        self.downloader = CrawlerDownloader()
        self.book = Book
        self.title = None

        self.language = 'en'
        self.images = {}
        self.pages = {}
        self.contents = {}
        self.article_counter = 1

    def _prepare_url(self, url):
        return url.replace('http:', '').replace('https:', '').strip('/')

    def _prepeare_name(self, url):
        return url.replace('/', '_')

    def _prepare_url_to_crawl(self, url):
        r = urlopen('http://' + url)
        return r.geturl()

    def _get_the_interface(self, interface):
        if interface:
            return interface
        else:
            return EmptyInterface()

    @staticmethod
    def _get_urlhash(url):
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        return m.hexdigest()

    def _get_filepath(self, url):
        return self.dirs.html + self._get_urlhash(url) + '.html'

    @staticmethod
    def _file_write(contents, filepath):
        html_file = open(filepath, "w+")
        html_file.write(contents)
        html_file.close()

    @staticmethod
    def _file_read(filepath):
        with open(filepath, 'r') as html_file:
            contents = html_file.read()
        return contents

    def _file_download(self, url, filepath):
        self.dirs._prepare_directories()
        response = urlopen(url)
        data = response.read()
        contents = data.decode('utf-8')
        self._file_write(contents, filepath)
        return contents

    def get_cover_title(self):
        cover_title = self.title + ' '
        if self.start == self.end:
            cover_title = cover_title + str(self.start)
        else:
            end_date = self.end.split(' ')
            start_date = self.start.split(' ')
            if len(end_date) == len(start_date):
                ed = []
                for i, d in enumerate(end_date):
                    if d != start_date[i]:
                        ed.append(d)
            ed = ' '.join(ed)
            cover_title = cover_title + ed + '-' + self.start
        return cover_title

    @staticmethod
    def get_date(str_date):
        return re.sub('[^\,]*, ', '', str_date)

    def _get_content(self, url):
        filepath = self._get_filepath(url)
        if self.force_download or not os.path.isfile(filepath):
            contents = self._file_download(url, filepath)
        else:
            contents = self._file_read(filepath)
        return contents

    def _get_blog_language(self, content):
        language = self.language;
        if re.search("'lang':[\s]*'([a-z^']+)'", content):
            language = re.search("'lang':[\s]*'([a-z^']+)'", content).group(1).strip()
        if re.search('lang="([a-z^"]+)"', content):
            language = re.search('lang="([a-z^"]+)"', content).group(1).strip()
        for arg in sys.argv:
            if arg.find('-ln=') == 0:
                language = arg.replace('-ln=', '')
            if arg.find('--language=') == 0:
                language = arg.replace('--language=', '')
        return language

    def _get_blog_title(self, content):
        return re.search("<title>([^>^<]*)</title>", content).group(1).strip()

    def _get_articles(self, content):
        """
        :param content: web page content
        :return: list of Article class objects
        """
        articles_list = re.findall("<h3 class='post-title entry-title' itemprop='name'>[\s]*<a href='([^']*)'>([^>^<]*)</a>[\s]*</h3>",
                          content)
        output = []
        for art in articles_list:
            output.append(Article(art[0], art[1], self._get_content, self.dirs, self.interface))
        return output

    def _get_url_to_crawl(self, content):
        url_to_crawl = None
        if re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'", content):
            url_to_crawl = re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'",
                                 content).group(1)
        return url_to_crawl

    def _articles_loop(self, articles):
        for art in articles:
            if self.skip == False or self.article_counter > self.skip:
                art.download(art.url)
                art.process()
                self.interface.print(str(self.ebook_article_counter) + '. ' + art.title)
                if self.start == False:
                    self.start = art.date
                self.end = art.date
                if len(art.date) == 1:
                    art_date = '<p><strong>' + art_date[0] + '</strong></p>'
                self.book.addChapter(art, self.language)
                self._check_limit()
            self.blog_article += 1

    def _check_limit(self):
        if self.limit and self.ebook_article > self.limit:
            self.url_to_crawl = None

    def crawl(self):
        while self.url_to_crawl:
            content = self._get_content(self.url_to_crawl)
            articles = self._get_articles(content)
            if len(self.book.chapters) == 0:
                self.language = self._get_blog_language(content)
                self.title = self._get_blog_title(content)
                self.book.set_language(self.language)
                self.book.add_author(self.title + ', ' + self.url)
            self._articles_loop(articles)
            self.url_to_crawl = self._get_url_to_crawl(content)

    def save(self):
        pass


class Dirs(object):
    """
    Tiny class to temporary directories configurations.
    """

    def _prepare_directories(self):
        paths = [self.html, self.images, self.originals]
        for p in paths:
            if not os.path.exists(p):
                os.makedirs(p)

    def __init__(self, name):
        self.path = './temp/' + name + '/'
        self.html = self.path + 'html/'
        self.images = self.path + 'images/'
        self.originals = self.path + 'originals/'
        self._prepare_directories()


class Article:
    """
    Blog post, article which became book chapter...
    """

    def __init__(self, url, title, download, dirs, interface, include_images=True):
        self.url = url
        self.title = title
        self.download = download
        self.interface = interface
        self.dirs = dirs
        self.comments = []
        self.include_images = include_images
        self.images = []
        self.images_files = []
        self.images_included = []
        self.html = None
        self.content = None
        self.date = None
        self.tree = None

    def _get_title(self):
        self.title = self.title.strip()

    def _get_date(self):
        self.date = self.tree.xpath('//h2[@class="date-header"]/span/text()')[0]

    def _image_download(self, picture_url, original_picture, target_picture):
        result = False
        if picture_url.startswith("//"):
            picture_url = "http:" + picture_url
        if not os.path.isfile(original_picture):
            try:
                u = urlopen(picture_url)
                f = open(original_picture, 'wb')
                block_sz = 8192
                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break
                    f.write(buffer)
                f.close()
            except Exception as e:
                self.interface.print(e)
        if self.include_images and not os.path.isfile(target_picture) and os.path.isfile(original_picture):
            try:
                picture = Image.open(original_picture)
                if picture.size[0] > self.images_width or picture.size[1] > self.images_height:
                    picture.thumbnail([self.images_width, self.images_height], Image.ANTIALIAS)
                picture = picture.convert('L')
                picture.save(target_picture, format='JPEG', quality=self.images_quality)
            except Exception as e:
                self.interface.print(e)
        if os.path.isfile(target_picture):
            result = True
        return result

    def _find_images(self):
        return re.findall(
            '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)',
            self.html)

    @staticmethod
    def _default_processor(html, im_url, im_hash, im_fname, dest_fname, im_regex=None):
        im_regex = '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="' + im_url +\
                   '"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">[^<]*</td></tr>[\s]*</tbody></table>'
        try:
            html = re.sub(im_regex, ' #blogspot2epubimage#' + im_hash + '# ', html)
        except Exception as e:
            print(e)
        return html

    @staticmethod
    def _nocaption_processor(html, im_url, im_hash, im_fname, dest_fname, im_regex=None):
        pass

    def _process_images(self, images=[], processor=_default_processor):
        for image in images:
            im_url = image[0]
            m = hashlib.md5()
            m.update(im_url)
            im_hash = m.hexdigest()
            self.images_included.append(im_hash + ".jpg")
            im_fname = self.dirs.originals + im_hash + ".jpg"
            dest_fname = self.dirs.images + im_hash+ ".jpg"
            self.html = processor(self.html, im_url, im_hash, im_fname, dest_fname)
            if self._image_download(image[0], im_fname, dest_fname):
                self.images_files.append(im_fname)

    def _get_images(self):
        self._process_images(self._find_images())
        self._get_tree()
        # self._process_images(self.tree.xpath('//a[@imageanchor="1"]'), self._nocaption_processor)
        # self._get_tree()

    def _replace_images(self):
        images_md5 = re.findall('#blogspot2epubimage#([^#]*)', self.content)
        for im_md5 in images_md5:
            for image in self.images:
                m = hashlib.md5()
                m.update(image[0])
                image_caption = image[1].strip().decode('utf-8')
                if m.hexdigest() == im_md5:
                    image_html = '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/' + im_md5 + '.jpg" /></td></tr><tr><td class="tr-caption" style="text-align: center;">' + image_caption + '</td></tr></tbody></table>'
                    self.content = self.content.replace('#blogspot2epubimage#' + im_md5 + '#', image_html)

    def _get_content(self):
        self.content = self.tree.xpath("//div[contains(concat(' ',normalize-space(@class),' '),'post-body')]")
        if len(self.content) == 1:
            self.content = self.content[0]
            self.content = ET.tostring(self.content)
            self.content = re.sub('style="[^"]*"', '', self.content.decode("utf-8"))
            self.content = re.sub('class="[^"]*"', '', self.content)

    def _get_tree(self):
        self.tree = fromstring(self.html)

    def _get_comments(self):
        """
        :param article: Article class
        :return:
        """
        headers = self.tree.xpath('//div[@id="comments"]/h4/text()')
        comments = ''
        if len(headers) == 1:
            art_comments = '<hr/><h4>' + headers[0] + '</h4>'
        art_comments_c = self.tree.xpath('//div[@class="comment-block"]//text()')
        tag = 'h3';
        for acc in art_comments_c:
            acc = acc.strip()
            if acc != 'Odpowiedz' and acc != 'Usuń':
                art_comments = art_comments + '<' + tag + '>' + acc + '</' + tag + '>'
                if tag == 'h3': tag = 'p'
            if acc == 'Usuń': tag = 'h3'
        return comments

    def process(self):
        self.html = self.download(self.url)
        self._get_tree()
        self._get_title()
        self._get_date()
        self._get_content()
        self._get_comments()


class CrawlerDownloader:

    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + str(buf)


class EmptyInterface:
    """
    Emty interface for script output.
    """

    @staticmethod
    def print(self):
        pass

    @staticmethod
    def exception(e):
        pass