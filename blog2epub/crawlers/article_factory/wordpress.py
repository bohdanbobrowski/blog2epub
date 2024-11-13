import re

from lxml import etree
from lxml.html.soupparser import fromstring

from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import ImageModel


class WordpressArticleFactory(DefaultArticleFactory):
    images_xpaths = [
        '//img[contains(@class, "size-full")]',
        '//figure[contains(@class, "wp-block-image")]//img',
        '//div[contains(@class, "wp-block-image")]//img',
        "//img",
    ]

    def get_images(self):
        images_list = self._get_images_with_captions()
        for x in self.images_xpaths:
            images_elements = self.tree.xpath(x)
            images_list.append(self._get_single_images(images_elements))
        # self._remove_images(images_html=images_html, images_list=images_list)
        self._insert_images(images_list=images_list)

    def _get_single_images(self, images_elements) -> list[ImageModel]:
        images_list = []
        for img in images_elements:
            img_url = img.attrib.get("data-orig-file")
            if not img_url:
                img_url = img.attrib.get("src")
            if img_url:
                img_url = img_url.split("?")[0]
                img_description = img.attrib.get("data-image-title")
                if not img_description:
                    img_description = img.attrib.get("title")
                if not img_description:
                    img_description = img.attrib.get("alt")
                image_obj = ImageModel(
                    url=img_url,
                    description=img_description,
                )
                if self.downloader.download_image(image_obj):
                    img_parent = img.getparent()
                    if img_parent:
                        img_parent.replace(img, etree.Comment(f"#blog2epubimage#{img_parent.hash}#"))
                        self.tree = img_parent.getroottree()
                    self.html = etree.tostring(self.tree).decode("utf-8")
                    images_list.append(image_obj)
        return images_list

    def _get_images_with_captions(self) -> list[ImageModel]:
        images_list = []
        for img in self.tree.xpath('//div[contains(@class, "wp-caption")]'):
            img_tr = fromstring(etree.tostring(img).decode("utf-8"))
            img_url = img_tr.xpath("//img/@src")[0]
            img_description = img_tr.xpath('//p[@class="wp-caption-text"]/text()').pop()
            image_obj = ImageModel(url=img_url, description=img_description)
            self.downloader.download_image(image_obj)
            img_parent = img.getparent()
            img_parent.replace(img, etree.Comment(f"#blog2epubimage#{image_obj.hash}#"))
            self.tree = img_parent.getroottree()
            self.html = etree.tostring(self.tree).decode("utf-8")
            images_list.append(image_obj)
        return images_list

    def get_content(self):
        article_header = re.findall(r"(<h1 class=\"entry-title\">[^<]*<\/h1>)", self.html)
        if article_header:
            self.html = self.html.split(article_header[0])[1]
        article_footer = re.findall(r"(<div id=\"atatags-[^\"]*\")", self.html)
        if article_footer:
            self.html = self.html.split(article_footer[0])[0]
        self.content = self.html = self.html.strip()
        self.tree = fromstring(self.html)

    def get_tags(self):
        pass
