#!/usr/bin/env python
# -*- coding: utf-8 -*-
# blogspot2epub
# version 0.2
# author: Bohdan Bobrowski bohdan@bobrowski.com.pl

import os
import json
import re
import sys
import pycurl
import urllib2
import hashlib
from ebooklib import epub
from slugify import slugify
from lxml import html
from lxml import etree
import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from os import listdir
from os.path import isfile, join

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

def getImages(html):
    images = []
    return images

def getDate(str_date):
    return unicode(re.sub('[^\,]*, ','',str_date))

# Default params:
INCLUDE_IMAGES = True
IMAGES_QUALITY = 40
IMAGES_HEIGHT = 300
IMAGES_WIDTH = 400
LIMIT = False
SKIP = False

# Check CLI params
if len(sys.argv) < 2:
    print "usage: blogspot2epub <blog_name> [params...]"
    exit();

# Read CLI params
if '-n' in sys.argv or '--no-images' in sys.argv:
    INCLUDE_IMAGES = False

for arg in sys.argv:
    if arg.find('-l=') == 0:
        LIMIT = int(arg.replace('-l=',''))
    if arg.find('--limit=') == 0:
        LIMIT = int(arg.replace('--limit=',''))
    if arg.find('-s=') == 0:
        SKIP = int(arg.replace('-s=',''))
    if arg.find('--skip=') == 0:
        SKIP = int(arg.replace('--skip=',''))
    if arg.find('-q=') == 0:
        IMAGES_QUALITY = int(arg.replace('-q=',''))
    if arg.find('--quality=') == 0:
        IMAGES_QUALITY = int(arg.replace('--quality=',''))

START_DATE = False;
END_DATE = False;

book = epub.EpubBook()
spistresci = []
y = x = 1
BLOG_URL = 'http://'+sys.argv[1]+'.blogspot.com/'
images_included = []
while BLOG_URL != '':
    www_html = DownloadWebPage(BLOG_URL)
    artykuly = re.findall("<h3 class='post-title entry-title' itemprop='name'>[\s]*<a href='([^']*)'>([^>^<]*)</a>[\s]*</h3>",www_html)
    if x == 1:
        title = re.search("<title>([^>^<]*)</title>",www_html).group(1).strip().decode('utf-8');
        book.set_title(unicode(title))
        book.set_language('pl')
        book.add_author(BLOG_URL)
        if not os.path.isfile(sys.argv[1]+'.jpg'):
            cover_image = Image.new('RGB', (600, 800))
            cover_draw = ImageDraw.Draw(cover_image)
            cover_draw.text((15, 700),title,(255,255,255),font=ImageFont.truetype("Lato-Bold.ttf", 35))
            cover_draw.text((15, 740),sys.argv[1]+".blogspot.com",(255,255,255),font=ImageFont.truetype("Lato-Regular.ttf", 25))
            cover_image.save(sys.argv[1]+'.jpg', format='JPEG', quality=100)
        book.set_cover(sys.argv[1]+'.jpg', open(sys.argv[1]+'.jpg', 'rb').read())
    BLOG_URL = ''
    if re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'",www_html):
        BLOG_URL = re.search("<a class='blog-pager-older-link' href='([^']*)' id='Blog1_blog-pager-older-link'",www_html).group(1)        
    for art in artykuly:
        if SKIP == False or y>SKIP:
            art_title = unicode(art[1].strip().decode('utf-8'))
            print str(x)+'. '+art_title
            art_html = DownloadWebPage(art[0])
            art_tree = html.fromstring(art_html)
            art_date = art_tree.xpath('//h2[@class="date-header"]/span/text()')        
            if START_DATE == False:
                START_DATE = getDate(art_date[0])
            END_DATE = getDate(art_date[0])
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
                    image_url = image[0]
                    originals_path = "./"+sys.argv[1]+"/originals/"
                    if not os.path.exists(originals_path):
                        os.makedirs(originals_path)
                    images_path = "./"+sys.argv[1]+"/images/"
                    if not os.path.exists(images_path):
                        os.makedirs(images_path)
                    m = hashlib.md5()
                    m.update(image_url)
                    image_hash = m.hexdigest()
                    images_included.append(image_hash+".jpg")
                    image_file_name = originals_path+image_hash+".jpg"
                    image_file_name_dest = images_path+image_hash+".jpg"
                    image_regex = '<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="'+image[0]+'"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">[^<]*</td></tr>[\s]*</tbody></table>'
                    art_html = re.sub(image_regex,' #blogspot2epubimage#'+image_hash+'# ',art_html)
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
                    if INCLUDE_IMAGES and not os.path.isfile(image_file_name_dest):
                        im = Image.open(image_file_name)
                        if im.size[0]>IMAGES_HEIGHT or im.size[1]>IMAGES_WIDTH:
                            im.thumbnail([IMAGES_HEIGHT,IMAGES_WIDTH], Image.ANTIALIAS)                        
                        # im = im.convert('L')
                        im = im.convert('L')
                        im.save(image_file_name_dest, format='JPEG', quality=IMAGES_QUALITY)
            art_tree = html.fromstring(art_html)        
            images_nocaption = art_tree.xpath('//a[@imageanchor="1"]')
            if len(images_nocaption) > 0:
                for image in images_nocaption:
                    image = etree.tostring(image)
                    image_href = re.findall('href="([^"]*)"',image)[0]
                    image_src = re.findall('src="([^"]*)"',image)[0]
                    if INCLUDE_IMAGES:
                        originals_path = "./"+sys.argv[1]+"/originals/"
                        if not os.path.exists(originals_path):
                            os.makedirs(originals_path)
                        images_path = "./"+sys.argv[1]+"/images/"
                        if not os.path.exists(images_path):
                            os.makedirs(images_path)
                        image_url = '';
                        if len(image_href) > 0:
                            image_url = image_href
                            image_regex = '<a href="'+image_url+'"[^>]*><img[^>]*></a>'
                        if len(image_src) > 0:
                            image_url = image_src
                            image_regex = '<img[?=\sa-z\"0-9]*src="'+image_url+'"[^>]+>'
                        if len(image_url) > 0:
                            m = hashlib.md5()
                            m.update(image_url)
                            image_hash = m.hexdigest()
                            images_included.append(image_hash+".jpg")
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
                                if im.size[0]>IMAGES_HEIGHT or im.size[1]>IMAGES_WIDTH:
                                    im.thumbnail([IMAGES_HEIGHT,IMAGES_WIDTH], Image.ANTIALIAS)
                                im = im.convert('L')
                                im.save(image_file_name_dest, format='JPEG', quality=IMAGES_QUALITY)
                    else:
                        art_html = art_html.replace(image,'')
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
                        image = etree.tostring(image)
                        image_href = re.findall('href="([^"]*)"',image)[0]
                        image_src = re.findall('src="([^"]*)"',image)[0]
                        image_url = ''
                        if len(image_href) > 0:
                            image_url = image_href
                        if len(image_src) > 0:
                            image_url = image_src
                        if len(image_url) > 0:
                            m = hashlib.md5()
                            m.update(image_url)
                            if m.hexdigest() == image_md5:
                                image_html = '<img border="0" src="images/'+image_md5+'.jpg" />'
                                art_content = art_content.replace('#blogspot2epubimage#'+image_md5+'#',image_html)
                        else:
                            art_content = art_content.replace('#blogspot2epubimage#'+image_md5+'#','<em>Image not found<em>')
                c.content = c.content+art_content
            c.content = c.content+art_comments
            book.add_item(c)        
            book.spine.append(c)
            spistresci.append(c)        
            x = x+1
            if not LIMIT == False and x>LIMIT:
                BLOG_URL = ''
                break
        y = y+1

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

# Add images do epub file_name
if INCLUDE_IMAGES:
    try:
        converted_images = [ f for f in listdir(images_path) if isfile(join(images_path,f)) ]
    except NameError:
        converted_images = []
    for i, image in enumerate(converted_images):
        if image in images_included:
            image_cont = None
            with open(images_path+image, 'r') as content_file:
                image_cont = content_file.read()
            epub_img = epub.EpubItem(uid="img"+str(i), file_name="images/"+image, media_type="image/jpeg", content=image_cont)
            book.add_item(epub_img)

# Save damn ebook
epub_fname = sys.argv[1]+'.blogspot.com'
if START_DATE == END_DATE:
    epub_fname = epub_fname+'_'+slugify(END_DATE)
else:
    end_date = END_DATE.split(' ')
    start_date = START_DATE.split(' ')
    if len(end_date) == len(start_date):
        ed = []
        for i,d in enumerate(end_date):
            if d != start_date[i]:
                ed.append(d)
    ed = '_'.join(ed)
    epub_fname = epub_fname+'_'+slugify(ed)+'-'+START_DATE.replace(' ','_')
epub_fname = slugify(epub_fname)
epub.write_epub(epub_fname+'.epub', book, {})
