#!/usr/bin/env python
# -*- coding: utf-8 -*-
# blogspot2epub
# version 0.1
# author: Bohdan Bobrowski bohdan@bobrowski.com.pl

import os
import json
import re
import sys
import pycurl
import urllib2
import hashlib
from ebooklib import epub
from lxml import html
from lxml import etree
import requests
from PIL import Image
from os import listdir
from os.path import isfile, join
import zipfile

class WWWDownloader:
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents = self.contents + buf

def DownloadWebPage(url):
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
        www_html = ''            
    else:
        www_html = www.contents
    return www_html


if len(sys.argv) > 1:
    book = epub.EpubBook()
    spistresci = []
    x = 1
    url_strony = 'http://'+sys.argv[1]+'.blogspot.com/'
    while url_strony != '':
        www_html = DownloadWebPage(url_strony)
        artykuly = re.findall("<h3 class='post-title entry-title' itemprop='name'>[\s]*<a href='([^']*)'>([^>^<]*)</a>[\s]*</h3>",www_html)
        if x == 1:
            book.set_title(unicode(re.search("<title>([^>^<]*)</title>",www_html).group(1).strip().decode('utf-8')))
            book.set_language('pl')
            book.add_author(url_strony)
            if os.path.isfile(sys.argv[1]+'.jpg'):
                book.set_cover(sys.argv[1]+'.jpg', open(sys.argv[1]+'.jpg', 'rb').read())
        url_strony = ''
        if re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link' title='Starsze posty'>Starsze posty</a>",www_html):
            url_strony = re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link' title='Starsze posty'>Starsze posty</a>",www_html).group(1)        
        for art in artykuly:
            art_title = unicode(art[1].strip().decode('utf-8'))
            print str(x)+'. '+art_title
            art_html = DownloadWebPage(art[0])
            art_tree = html.fromstring(art_html)
            art_date = art_tree.xpath('//h2[@class="date-header"]/span/text()')
            if len(art_date) == 1:
                art_date = '<p><strong>'+art_date[0]+'</strong></p>'            
            art_comments_h = art_tree.xpath('//div[@id="comments"]/h4/text()')
            art_comments = ''
            if len(art_comments_h) == 1:
                art_comments = '<hr/><h4>'+art_comments_h[0]+'</h4>'
            art_comments_c = art_tree.xpath('//div[@class="comment-block"]//text()')
            tag=u'h3';
            for acc in art_comments_c:
                acc = acc.strip()
                if acc != u'Odpowiedz' and acc != u'Usuń':
                    art_comments = art_comments+u'<'+tag+u'>'+acc+ u'</'+tag+u'>'
                    if tag == u'h3': tag = u'p'
                if acc == u'Usuń': tag = u'h3'
            c = epub.EpubHtml(title=art_title, file_name='chap_'+str(x)+'.xhtml', lang='pl')
            # Post title:
            c.content = u'<h2>'+art_title+u'</h2>'+art_date+u'<p><i>'+art[0]+u'</i></p>'
            # Images:
            images = re.findall('<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)',art_html)
            if len(images) > 0:
                for image in images:
                    originals_path = "./"+sys.argv[1]+"/originals/"
                    if not os.path.exists(originals_path):
                        os.makedirs(originals_path)
                    images_path = "./"+sys.argv[1]+"/images/"
                    if not os.path.exists(images_path):
                        os.makedirs(images_path)
                    m = hashlib.md5()
                    m.update(image_url)
                    image_hash = m.hexdigest()
                    image_file_name = originals_path+image_hash+".jpg"
                    image_file_name_dest = images_path+image_hash+".jpg"
                    image_regex = '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="'+image[0]+'"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">[^<]*</td></tr>[\s]*</tbody></table>'
                    art_html = re.sub(image_regex,' #blogspot2epubimage#'+m.image_hash+'# ',art_html)
                    if not os.path.isfile(image_file_name):
                        try:
                            u = urllib2.urlopen(image[0])
                            f = open(image_file_name, 'wb')
                            block_sz = 8192
                            while True:
                                buffer = u.read(block_sz)
                                if not buffer:
                                    break
                                f.write(buffer)
                            f.close()
                        except urllib2.HTTPError as e:
                            print(e.code)
                            print(e.read())
                    if not os.path.isfile(image_file_name_dest):
                        im = Image.open(image_file_name)
                        if im.size[0]>600 or im.size[1]>800:
                            im.thumbnail([600,800], Image.ANTIALIAS)
                        im = im.convert('L')
                        im.save(image_file_name_dest)
            art_tree = html.fromstring(art_html)
            images_nocaption = art_tree.xpath('//a[@imageanchor="1"]')
            if len(images_nocaption) > 0:
                for image in images_nocaption:
                    originals_path = "./"+sys.argv[1]+"/originals/"
                    if not os.path.exists(originals_path):
                        os.makedirs(originals_path)
                    images_path = "./"+sys.argv[1]+"/images/"
                    if not os.path.exists(images_path):
                        os.makedirs(images_path)
                    image = etree.tostring(image)
                    image_url = re.findall('href="([^"]*)"',image)
                    if len(image_url) > 0:
                        image_url = image_url[0]
                        m = hashlib.md5()
                        m.update(image_url)
                        image_hash = m.hexdigest()
                        image_regex = '<a href="'+image_url+'"[^>]*><img[^>]*></a>'
                        art_html = re.sub(image_regex,' #blogspot2epubimage#'+image_hash+'# ',art_html)
                        image_file_name = originals_path+image_hash+".jpg"
                        image_file_name_dest = images_path+image_hash+".jpg"
                        if not os.path.isfile(image_file_name):
                            try:
                                u = urllib2.urlopen(image_url)
                                f = open(image_file_name, 'wb')
                                block_sz = 8192
                                while True:
                                    buffer = u.read(block_sz)
                                    if not buffer:
                                        break
                                    f.write(buffer)
                                f.close()
                            except urllib2.HTTPError as e:
                                print(e.code)
                                print(e.read())
                        if not os.path.isfile(image_file_name_dest):
                            im = Image.open(image_file_name)
                            if im.size[0]>600 or im.size[1]>800:
                                im.thumbnail([600,800], Image.ANTIALIAS)
                            im = im.convert('L')
                            im.save(image_file_name_dest)
            # Post content:
            art_tree = html.fromstring(art_html)
            art_content = art_tree.xpath("//div[contains(concat(' ',normalize-space(@class),' '),'post-body')]")
            if len(art_content) == 1:
                art_content = etree.tostring(art_content[0], pretty_print=True)
                art_content = re.sub('style="[^"]*"', '', art_content)
                art_content = re.sub('class="[^"]*"', '', art_content)
                images_md5 = re.findall('#blogspot2epubimage#([^#]*)',art_content)
                for image_md5 in images_md5:
                    for image in images:
                        m = hashlib.md5()
                        m.update(image[0])
                        image_caption = image[1].strip().decode('utf-8')
                        if m.hexdigest() == image_md5:
                            image_html = '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/'+image_md5+'.jpg" /></td></tr><tr><td class="tr-caption" style="text-align: center;">'+image_caption+'</td></tr></tbody></table>'
                            art_content = art_content.replace('#blogspot2epubimage#'+image_md5+'#',image_html)
                    for image in images_nocaption:
                        m = hashlib.md5()
                        m.update(image_url)
                        if m.hexdigest() == image_md5:
                            image_html = '<img border="0" src="images/'+image_md5+'.jpg" />'
                            art_content = art_content.replace('#blogspot2epubimage#'+image_md5+'#',image_html)
                c.content = c.content+art_content
            c.content = c.content+art_comments
            book.add_item(c)        
            book.spine.append(c)
            spistresci.append(c)        
            x = x+1
            # if x>10:
            #     url_strony = ''
            #     break
            # book.toc = (epub.link('chap_01.xhtml', 'introduction', 'intro'),(epub.Section('Simple book'),(c1, )))

    # Add cover - if file exist
    book.spine.append('nav')
    if os.path.isfile(sys.argv[1]+'.jpg'):
        book.spine.append('cover')       
    book.spine.reverse()
    spistresci.reverse()
    book.toc = spistresci

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
    epub.write_epub(sys.argv[1]+'_blogspot_com.epub', book, {})

    # Add images do epub file
    try:
        converted_images = [ f for f in listdir(images_path) if isfile(join(images_path,f)) ]
    except NameError:
        converted_images = []
    zip_file = zipfile.ZipFile(sys.argv[1]+'_blogspot_com.epub', 'a')
    for image in converted_images:
        zip_file.write(images_path+image, "EPUB\\images\\"+image, zipfile.ZIP_DEFLATED )
