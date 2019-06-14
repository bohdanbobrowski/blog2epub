#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import hashlib
import html
import os
import re
from urllib.request import urlopen
from lxml.html.soupparser import fromstring
from lxml.ElementInclude import etree
from PIL import Image

from blog2epub.Book import Book


class Crawler(object):
    """
    Universal blog crawler.
    """

    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'

    def __init__(self, url, include_images=True, images_height=800, images_width=600, images_quality=40, start=None,
                 end=None, limit=None, skip=False, force_download=False, file_name=None, destination_folder='./',
                 language=None, interface=None):

        self.url = self._prepare_url(url)
        self.url_to_crawl = self._prepare_url_to_crawl(self.url)
        self.file_name = self._prepare_file_name(file_name, self.url)
        self.destination_folder = destination_folder
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
        self.book = None
        self.title = None
        self.description = None
        self.language = language
        self.articles = []
        self.article_counter = 0
        self.images = []
        self.downloader = Downloader(self)

    def _prepare_url(self, url):
        return url.replace('http:', '').replace('https:', '').strip('/')

    def _prepare_file_name(self, file_name, url):
        if file_name:
            return file_name
        return url.replace('/', '_')

    def _prepare_url_to_crawl(self, url):
        r = urlopen('http://' + url)
        return r.geturl()

    def _get_the_interface(self, interface):
        if interface:
            return interface
        else:
            return EmptyInterface()

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

    def _get_blog_language(self, content):
        if self.language is None and re.search("'lang':[\s]*'([a-z^']+)'", content):
            self.language = re.search("'lang':[\s]*'([a-z^']+)'", content).group(1).strip()
        if self.language is None and re.search('lang=[\'"]([a-z]+)[\'"]', content):
            self.language = re.search('lang=[\'"]([a-z]+)[\'"]', content).group(1).strip()
        if self.language is None and re.search('locale[\'"]:[\s]*[\'"]([a-z]+)[\'"]', content):
            self.language = re.search('locale[\'"]:[\s]*[\'"]([a-z]+)[\'"]', content).group(1).strip()
        if self.language is None:
            self.language = 'en';

    def _get_blog_title(self, content):
        return re.search("<title>([^>^<]*)</title>", content).group(1).strip()

    def _get_blog_description(self, tree):
        return tree.xpath('//div[@id="header"]/div/div/div/p[@class="description"]/span/text()')

    def _get_header_images(self, tree):
        header_images = []
        for img in tree.xpath('//div[@id="header"]/div/div/div/p[@class="description"]/span/img/@src'):
            header_images.append(self.downloader.download_image(img))
        return header_images

    def _get_articles(self, content):
        """
        :param content: web page content
        :return: list of Article class objects
        """
        articles_list = re.findall("<h3 class='post-title entry-title' itemprop='name'>[\s]*<a href='([^']*)'>([^>^<]*)</a>[\s]*</h3>",
                          content)
        output = []
        for art in articles_list:
            output.append(Article(art[0], art[1], self))
        return output

    def _get_url_to_crawl(self, tree):
        url_to_crawl = None
        if tree.xpath('//a[@class="blog-pager-older-link"]/@href'):
            url_to_crawl = tree.xpath('//a[@class="blog-pager-older-link"]/@href')[0]
        return url_to_crawl

    def _articles_loop(self, content):
        articles = self._get_articles(content)
        for art in articles:
            self.article_counter += 1
            if not self.skip or self.article_counter > self.skip:
                art.process()
                self.images = self.images + art.images
                self.interface.print(str(len(self.articles) + 1) + '. ' + art.title)
                if self.start:
                    self.end = art.date
                else:
                    self.start = art.date
                self.articles.append(art)
                self._check_limit()
            if not self.url_to_crawl:
                break

    def _check_limit(self):
        if self.limit and len(self.articles) >= self.limit:
            self.url_to_crawl = None

    def _crawl(self):
        while self.url_to_crawl:
            content = self.downloader.get_content(self.url_to_crawl)
            tree = fromstring(content)
            if len(self.articles) == 0:
                self._get_blog_language(content)
                self.title = self._get_blog_title(content)
                self.images = self.images +self._get_header_images(tree)
                self.description = self._get_blog_description(tree)
            self._articles_loop(content)
            self.url_to_crawl = self._get_url_to_crawl(tree)
            self._check_limit()

    def save(self):
        self._crawl()
        self.book = Book(self)
        self.book.save()


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
        self.assets = './assets/'
        self._prepare_directories()


class Downloader(object):

    def __init__(self, crawler):
        self.dirs = crawler.dirs
        self.force_download = crawler.force_download
        self.images_width = crawler.images_width
        self.images_height = crawler.images_height
        self.images_quality = crawler.images_quality

    @staticmethod
    def get_urlhash(url):
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        return m.hexdigest()

    @staticmethod
    def file_write(contents, filepath):
        html_file = open(filepath, "w")
        html_file.write(contents)
        html_file.close()

    @staticmethod
    def file_read(filepath):
        with open(filepath, 'r') as html_file:
            contents = html_file.read()
        return contents

    def get_filepath(self, url):
        return self.dirs.html + self.get_urlhash(url) + '.html'

    def file_download(self, url, filepath):
        self.dirs._prepare_directories()
        response = urlopen(url)
        data = response.read()
        contents = data.decode('utf-8')
        self.file_write(contents, filepath)
        return contents

    def image_download(self, url, filepath):
        try:
            self.dirs._prepare_directories()
            f = open(filepath, 'wb')
            f.write(urlopen(url).read())
            f.close()
            return True
        except Exception as e:
            return False

    def get_content(self, url):
        filepath = self.get_filepath(url)
        if self.force_download or not os.path.isfile(filepath):
            contents = self.file_download(url, filepath)
        else:
            contents = self.file_read(filepath)
        return contents

    def download_image(self, img):
        if img.startswith("//"):
            img = "http:" + img
        img_hash = self.get_urlhash(img)
        img_type = os.path.splitext(img)[1].lower()
        img_filename = os.path.join(self.dirs.originals, img_hash + "." + img_type)
        if os.path.isfile(img_filename) or self.image_download(img, img_filename):
            img_images = os.path.join(self.dirs.images, img_hash + ".jpg")
            if not os.path.isfile(img_images):
                if os.path.isfile(img_filename):
                    try:
                        picture = Image.open(img_filename)
                        if picture.size[0] > self.images_width or picture.size[1] > self.images_height:
                            picture.thumbnail([self.images_width, self.images_height], Image.ANTIALIAS)
                        picture = picture.convert('L')
                        picture.save(img_images, format='JPEG', quality=self.images_quality)
                    except Exception as e:
                        return None
        return img_hash + ".jpg"


class Article(object):
    """
    Blog post, article which became book chapter...
    """

    def __init__(self, url, title, crawler):
        self.url = url
        self.title = title
        self.interface = crawler.interface
        self.dirs = crawler.dirs
        self.comments = ''
        self.include_images = crawler.include_images
        self.images_regex = crawler.images_regex
        self.images = []
        self.images_captions = []
        self.html = None
        self.content = None
        self.date = None
        self.tree = None
        self.downloader = Downloader(crawler)

    def _get_title(self):
        self.title = html.unescape(self.title.strip())

    def _get_date(self):
        self.date = re.sub('(.*?, )', '', self.tree.xpath('//h2[@class="date-header"]/span/text()')[0])

    def _find_images(self):
        return re.findall(self.images_regex, self.html)

    @staticmethod
    def _default_ripper(img, img_hash, html):
        im_regex = '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="' + img.replace("+", "\+") +\
                   '"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">[^<]*</td></tr>[\s]*</tbody></table>'
        try:
            return re.sub(im_regex, ' #blog2epubimage#' + img_hash + '# ', html)
        except Exception as e:
            print(e)

    @staticmethod
    def _nocaption_ripper(img, img_hash, html):
        im_regex = '<a href="' + img.replace("+", "\+") + '" imageanchor="1"[^<]*<img.*?></a>'
        try:
            return re.sub(im_regex, ' #blog2epubimage#' + img_hash + '# ', html)
        except Exception as e:
            print(e)

    @staticmethod
    def _bloggerphoto_ripper(img, img_hash, html):
        im_regex = '<a href="[^"]+"><img.*?id="BLOGGER_PHOTO_ID_[0-9]+".*?src="' + img.replace("+", "\+") + '".*?></a>'
        try:
            return re.sub(im_regex, ' #blog2epubimage#' + img_hash + '# ', html)
        except Exception as e:
            print(e)

    @staticmethod
    def _img_ripper(img, img_hash, html):
        im_regex = '<img.*?src="' + img.replace("+", "\+") + '".*?>'
        try:
            return re.sub(im_regex, ' #blog2epubimage#' + img_hash + '# ', html)
        except Exception as e:
            print(e)

    def _process_images(self, images, ripper):
        for image in images:
            if isinstance(image, str):
                img = image
                caption  = ''
            else:
                img = image[0]
                caption = image[1]
            img_hash = self.downloader.download_image(img)
            if img_hash:
                self.html = ripper(img=img, img_hash=img_hash, html=self.html)
                self.images.append(img_hash)
                self.images_captions.append(caption)
        self._get_tree()

    def _get_images(self):
        self._process_images(self._find_images(), self._default_ripper)
        self._process_images(self.tree.xpath('//a[@imageanchor="1"]/@href'), self._nocaption_ripper)
        self._process_images(self.tree.xpath('//img[contains(@id,"BLOGGER_PHOTO_ID_")]/@src'), self._bloggerphoto_ripper)
        self._process_images(self.tree.xpath('//img/@src'), self._bloggerphoto_ripper)
        self._replace_images()
        self._get_tree()

    def _replace_images(self):
        for key, image in enumerate(self.images):
            image_caption = self.images_captions[key]
            image_html = '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/' + image + '" /></td></tr><tr><td class="tr-caption" style="text-align: center;">' + image_caption + '</td></tr></tbody></table>'
            self.html = self.html.replace('#blog2epubimage#' + image + '#', image_html)

    def _get_content(self):
        self.content = self.tree.xpath("//div[contains(concat(' ',normalize-space(@class),' '),'post-body')]")
        if len(self.content) == 1:
            self.content = self.content[0]
            self.content = etree.tostring(self.content)
            self.content = re.sub('style="[^"]*"', '', self.content.decode("utf-8"))
            self.content = re.sub('class="[^"]*"', '', self.content)
            iframe_srcs = re.findall('<iframe.+? src="([^?= ]*)', self.content)
            for src in iframe_srcs:
                self.content = re.sub('<iframe.+?%s.+?/>' % src, '<a href="%s">%s</a>' % (src, src), self.content)

    def _get_tree(self):
        self.tree = fromstring(self.html)

    def _get_comments(self):
        """
        :param article: Article class
        :return:
        """
        headers = self.tree.xpath('//div[@id="comments"]/h4/text()')
        self.comments = ''
        if len(headers) == 1:
            self.comments = '<hr/><h3>' + headers[0] + '</h3>'
        comments_in_article = self.tree.xpath('//div[@class="comment-block"]//text()')
        tag = 'h5';
        for c in comments_in_article:
            c = c.strip()
            if c != 'Odpowiedz' and c != 'Usuń':
                self.comments = self.comments + '<' + tag + '>' + c + '</' + tag + '>'
                if tag == 'h5': tag = 'p'
            if c == 'Usuń': tag = 'h5'

    def process(self):
        self.html = self.downloader.get_content(self.url)
        self._get_tree()
        self._get_title()
        self._get_date()
        self._get_images()
        self._get_content()
        self._get_comments()


class EmptyInterface(object):
    """
    Emty interface for script output.
    """

    @staticmethod
    def print(self):
        pass

    @staticmethod
    def exception(e):
        pass