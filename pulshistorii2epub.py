#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pulshistorii2epub
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
from slugify import slugify

images_path = "./"+sys.argv[1]+"/images/"

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


def getArticles(tag_id):
    articles = []
    next_page = True
    next_page_param = ''
    while next_page != '':
        www_html = DownloadWebPage('http://pulshistorii.pb.pl/tag/'+tag_id+next_page_param)
        articles = articles + re.findall("<h2><a href=\"(/[0-9]+,[0-9]+,[^\"]+)\">([^<]+)",www_html)
        if re.search("<a href=\"([^\"]+)\">Następna &gt;</a>",www_html):
            next_page = re.search("<a href=\"([^\"]+)\">Następna &gt;</a>",www_html).group(1)
            next_page_param = next_page
        else:
            next_page = next_page_param = ''
    articles_and_title = {}
    filtered_articles = [];
    for key, art in enumerate(articles):
        if art[1].find("(WIDEO)") == -1 and art[1].find("(GALERIA)") == -1:
            filtered_articles.append(art)
    articles_and_title['articles'] = filtered_articles
    articles_and_title['title'] = 'Puls Historii - ' + re.search("<title>([^|]+)",www_html).group(1).strip().decode('utf-8')
    return articles_and_title

def downloadImages(images):
    for image in images:
        if type(image) is str:
            image_url = image
        else:
            image_url = 'http:'+image[0]
        image_url = image_url.replace('https','http')
        image_url = image_url.replace('w_200.jpg','w_600.jpg')
        originals_path = "./"+sys.argv[1]+"/originals/"
        if not os.path.exists(originals_path):
            os.makedirs(originals_path)
        if not os.path.exists(images_path):
            os.makedirs(images_path)
        m = hashlib.md5()
        m.update(image_url)
        image_hash = m.hexdigest()
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

def addImagesToArticle(images, art_content):
    for image in images:
        image_url = 'http:'+image[0]
        image_url = image_url.replace('w_200.jpg','w_600.jpg')
        m = hashlib.md5()
        m.update(image_url)
        image_hash = m.hexdigest()
        image_caption = image[1].strip().decode('utf-8')
        image_html = '<p><table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/'+image_hash+'.jpg" /></td></tr><tr><td class="tr-caption" style="text-align: center;">'+image_caption+'</td></tr></tbody></table></p>'
        art_content = art_content + image_html
    return art_content

def getGalleryImages(art_html, art_content):
    images = re.findall('<img src="(//static.pb.pl/filtered/[^/]+/[0-9]+,[0-9]+,w_200.jpg)" alt="([^"]+)"',art_html)
    if len(images) > 0:
        downloadImages(images)
        art_content = addImagesToArticle(images, art_content)
    return art_content
   
def getContentImages(art_content):
    images = re.findall('<img src="([^"]+)"',art_content)
    if len(images) > 0:
        downloadImages(images)
        for image in images:
            image_url = image.replace('https','http')
            m = hashlib.md5()
            m.update(image_url)
            image_hash = m.hexdigest()           
            art_content = art_content.replace(image,'images/'+image_hash+'.jpg')
    return art_content

if len(sys.argv) > 1:
    book = epub.EpubBook()
    spistresci = []
    url_strony = 'http://pulshistorii.pb.pl/tag/'+sys.argv[1]
    articles_and_title = getArticles(sys.argv[1])
    articles = articles_and_title['articles']
    book.set_title(unicode(articles_and_title['title']))
    book.set_language('pl')
    book.add_author(articles_and_title['title'] + " - " + url_strony)
    if os.path.isfile(sys.argv[1]+'.jpg'):
        book.set_cover(sys.argv[1]+'.jpg', open(sys.argv[1]+'.jpg', 'rb').read())
    x = 1
    for art in articles:
        art_title = unicode(art[1].strip().decode('utf-8'))
        print str(x)+'. '+art_title
        art_html = DownloadWebPage('http://pulshistorii.pb.pl'+art[0])
        art_tree = html.fromstring(art_html)
        art_date = art_tree.xpath('//span[@class="article_date"]/text()')
        if len(art_date) == 1:
            art_date = '<p><strong>'+art_date[0]+'</strong></p>'            
        c = epub.EpubHtml(title=art_title, file_name='chap_'+str(x)+'.xhtml', lang='pl')
        # Post title:
        c.content = u'<h2>'+art_title+u'</h2>'+art_date+u'<p><i>'+art[0]+u'</i></p>'
        # Post content:
        bad_content = ['h1','script','iframe','div[@id="article-header"]','div[@class="pictures"]']
        for b in bad_content:
            for bad in art_tree.xpath('//'+b):
                bad.getparent().remove(bad)
        # Clear content from unnecessary tags etc
        art_content = art_tree.xpath('//div[@class="content"]')
        if len(art_content) == 1:
            art_content = etree.tostring(art_content[0], pretty_print=True)
            art_content = art_content.replace("&#13;","");
            art_content = art_content.replace("</div>","");
            art_content = re.sub('style="[^"]*"', '', art_content)
            art_content = re.sub('class="[^"]*"', '', art_content)
            art_content = re.sub('<div[^<]+>', '', art_content)
        # Images:
        art_content = getGalleryImages(art_html, art_content)
        art_content = getContentImages(art_content);
        c.content = c.content+art_content
        book.add_item(c)        
        book.spine.append(c)
        spistresci.append(c)        
        x = x+1

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

    # Add images do epub file
    try:
        converted_images = [ f for f in listdir(images_path) if isfile(join(images_path,f)) ]
    except NameError:
        converted_images = []
    for i, image in enumerate(converted_images):
        image_cont = None
        with open(images_path+image, 'r') as content_file:
            image_cont = content_file.read()
        epub_img = epub.EpubItem(uid="img"+str(i), file_name="images/"+image, media_type="image/jpeg", content=image_cont)
        book.add_item(epub_img)

    # Write epub file
    epub.write_epub(slugify(articles_and_title['title']) + '.epub', book, {})
