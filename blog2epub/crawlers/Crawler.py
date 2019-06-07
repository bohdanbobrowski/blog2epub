#!/usr/bin/env python3
# -*- coding : utf-8 -*-

import hashlib
import html
import os
import re
import sys
from xml import etree

import pycurl
from ebooklib import epub
from PIL import Image


class Crawler(object):
    """
    Universal blog crawler.
    """

    def __init__(self, url, include_images=True, images_height=800, images_width=600, images_quality=40, start=None,
                 end=None, limit=False, skip=False, force_download=False, interface=None):
        self.url = url
        self.include_images = include_images
        self.images_quality = images_quality
        self.images_height = images_height
        self.images_width = images_width
        self.start = start
        self.end = end
        self.limit = limit
        self.skip = skip
        self.force_download = force_download

        if interface:
            self.interface = interface
        else:
            self.interface = EmptyInterface()

        self.downloader = CrawlerDownloader()
        self.path = './' + sys.argv[1] + '/'
        self.html_path = self.path + 'html/'
        self.book = epub.EpubBook()
        self.title = None
        self.url_to_crawl = None
        self.language = 'en'
        self.images = {}
        self.pages = {}
        self.contents = {}
        self.ebook_article_counter = self.blog_article_counter = 1

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
            self.interface.print(err)
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

    def _get_content(self, url, forceDownload=False):
        filepath = self._get_filepath(url)
        if forceDownload or not os.path.isfile(filepath):
            contents = self._file_download(url)
        else:
            contents = self._file_read()
        return contents

    def _get_blog_language(self, content):
        language = self.language;
        if re.search("'lang':[\s]*'([a-z^']+)'", content):
            language = re.search("'lang':[\s]*'([a-z^']+)'", content).group(1).strip().decode('utf-8')
        if re.search('lang="([a-z^"]+)"', content):
            language = re.search('lang="([a-z^"]+)"', content).group(1).strip().decode('utf-8')
        for arg in sys.argv:
            if arg.find('-ln=') == 0:
                language = arg.replace('-ln=', '')
            if arg.find('--language=') == 0:
                language = arg.replace('--language=', '')
        return language

    def _get_blog_title(self, content):
        return re.search("<title>([^>^<]*)</title>", content).group(1).strip().decode('utf-8')

    def _get_articles(self, content):
        return re.findall("<h3 class='post-title entry-title' itemprop='name'>[\s]*<a href='([^']*)'>([^>^<]*)</a>[\s]*</h3>",
                          content)

    def _get_article_title(self, article, content=None):
        return html.unescape(art[1].strip().decode('utf-8'))

    def _get_article_date(self, article, content):
        pass

    def _get_article_content(self, article, content):
        pass

    def _get_article_comments(self, article, content):
        pass

    def _get_url_to_crawl(self, content):
        url_to_crawl = None
        if re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'", content):
            url_to_crawl = re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'",
                                 content).group(1)
        return url_to_crawl

    def _articles_loop(self, articles):
        for art in articles:
            if self.skip == False or self.blog_article_counter > self.skip:
                content = self.download_web_page(art[0])
                art_tree = html.fromstring(content)

                art_title = self._get_article_title(art, content)
                self.interface.print(str(self.ebook_article_counter) + '. ' + art_title)

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
                c = epub.EpubHtml(title=art_title, file_name='chap_' + str(ebook_article) + '.xhtml', lang='pl')
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
                            self.interface.print(e)
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
                                    art_html = re.sub(image_regex, ' #blogspot2epubimage#' + image_hash + '# ',
                                                      art_html)
                                    image_file_name = originals_path + image_hash + ".jpg"
                                    image_file_name_dest = images_path + image_hash + ".jpg"
                                    if download_image(image_url, image_file_name, image_file_name_dest):
                                        image_files.append(image_file_name)
                                except Exception as err:
                                    self.interface.print(err)
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
                                    art_content = art_content.replace('#blogspot2epubimage#' + image_md5 + '#',
                                                                      image_html)
                            else:
                                art_content = art_content.replace('#blogspot2epubimage#' + image_md5 + '#',
                                                                  '<em>Image not found<em>')
                    c.content = c.content + art_content
                c.content = c.content + art_comments
                self.book.add_item(c)
                self.book.spine.append(c)
                self.table_of_contents.append(c)
                self.ebook_article += 1

                self._check_limit()
                self.images = image_files + self.images
            self.blog_article += 1

    def _check_limit(self):
        if self.limit and self.ebook_article > self.limit:
            self.url_to_crawl = None
            break

    def crawl(self):
        self.url_to_crawl = self.url
        while self.url_to_crawl:
            content = self.download_web_page(self.url_to_crawl, True)
            articles = self._get_articles(content)
            if self.ebook_article_counter == 1:
                self.language = self._get_blog_language(content)
                self.title = self._get_blog_title(content)
                self.book.set_language(self.language)
                self.book.add_author(self.title + ', ' + self.url)
            self._articles_loop(articles)
            self.url_to_crawl = self._get_url_to_crawl(content)

    def save(self):
        pass


class Article:

    def __init__(self, title, url):
        self.title = title
        self.url = url


class CrawlerDownloader:

    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf


class EmptyInterface:

    def print(self):
        pass