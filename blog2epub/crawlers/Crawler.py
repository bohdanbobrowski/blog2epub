#!/usr/bin/env python3
# -*- coding : utf-8 -*-

import hashlib
import html
import os
import re
import sys

import pycurl
from ebooklib import epub
from PIL import Image


class Crawler(object):
    """
    Universal blog crawler.
    """

    title = None
    language = 'en'
    images = {}
    pages = {}
    contents = {}

    def __init__(self, url, include_images=True, images_height=800, images_width=600, images_quality=40, start=None,
                 end=None, limit=False, skip=False):
        self.url = url
        self.include_images = include_images
        self.images_quality = images_quality
        self.images_height = images_height
        self.images_width = images_width
        self.start = start
        self.end = end
        self.limit = limit
        self.skip = skip
        self.downloader = CrawlerDownloader()
        self.path = './' + sys.argv[1] + '/'
        self.html_path = self.path + 'html/'
        self.book = epub.EpubBook()

    def _prepare_directories(self):
        if not os.path.exists(self.html_path):
            os.makedirs(self.html_path)

    @staticmethod
    def _get_urlhash(url):
        m = hashlib.md5()
        m.update(url)
        return m.hexdigest()

    def _get_filepath(self, url):
        return self.html_path + self._get_urlhash(url) + '.html'

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

    def _file_download(self, url):
        try:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEFUNCTION, self.downloader.body_callback)
            c.setopt(c.HEADER, 1);
            c.setopt(c.FOLLOWLOCATION, 1)
            c.setopt(c.COOKIEFILE, '')
            c.setopt(c.CONNECTTIMEOUT, 30)
            c.setopt(c.TIMEOUT, 30)
            c.setopt(c.COOKIEFILE, '')
            c.perform()
        except Exception as err:
            print(err)
            exit()
        else:
            contents = self.downloader.contents
            self._file_write(contents)
        return contents

    def _image_download(self, picture_url, original_picture, target_picture, urllib2=None):
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
                print(e)
        if self.include_images and not os.path.isfile(target_picture) and os.path.isfile(original_picture):
            try:
                picture = Image.open(original_picture)
                if picture.size[0] > self.images_width or picture.size[1] > self.images_height:
                    picture.thumbnail([self.images_width, self.images_height], Image.ANTIALIAS)
                picture = picture.convert('L')
                picture.save(target_picture, format='JPEG', quality=self.images_quality)
            except Exception as e:
                print(e)
        if os.path.isfile(target_picture):
            result = True
        return result

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

    def get_content(self, url, forceDownload=False):
        filepath = self._get_filepath(url)
        if forceDownload or not os.path.isfile(filepath):
            contents = self._file_download(url)
        else:
            contents = self._file_read()
        return contents

    def get_blog_language(self, html):
        language = self.language;
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

    def HTMLEntitiesToUnicode(text):
        return html.unescape(text)

    def crawl(self):
        url_to_crawl = self.url
        while url_to_crawl:
            url_to_crawl= None

class CrawlerDownloader:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf