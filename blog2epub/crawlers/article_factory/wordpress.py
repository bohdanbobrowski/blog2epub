import re
from xml.etree.ElementTree import fromstring

from lxml import etree

from blog2epub.crawlers.article_factory.default import DefaultArticleFactory
from blog2epub.models.book import ArticleModel, ImageModel


class WordpressArticleFactory(DefaultArticleFactory):
    images_xpaths = [
        '//img[contains(@class, "size-full")]',
        '//figure[contains(@class, "wp-block-image")]//img',
        '//div[contains(@class, "wp-block-image")]//img',
        "//img",
    ]

    def get_images(self):
        self.get_images_with_captions()
        for x in self.images_xpaths:
            imgs = self.tree.xpath(x)
            self.get_single_images(imgs)
        self.replace_images()
        self.get_tree()

    def get_single_images(self, images) -> list[ImageModel]:
        images_list = []
        for img in images:
            img_url = img.attrib.get("data-orig-file")
            if not img_url:
                img_url = img.attrib.get("src")
            if img_url:
                img_url = img_url.split("?")[0]
                img_caption = img.attrib.get("data-image-title")
                if not img_caption:
                    img_caption = img.attrib.get("title")
                if not img_caption:
                    img_caption = img.attrib.get("alt")
                img_hash = self.downloader.download_image(img_url)

                if img_hash:
                    img_parent = img.getparent()
                    if img_parent:
                        if img_hash:
                            img_parent.replace(img, etree.Comment(f"#blog2epubimage#{img_hash}#"))
                        else:
                            img_parent.text = ""
                        self.tree = img_parent.getroottree()
                    self.html = etree.tostring(self.tree).decode("utf-8")
                    images_list.append(
                        ImageModel(
                            url=img_url,
                            hash=img_hash,
                            description=img_caption,
                        )
                    )
        return images_list

    def get_images_with_captions(self):
        images_c = self.tree.xpath('//div[contains(@class, "wp-caption")]')
        for img in images_c:
            img_html = etree.tostring(img).decode("utf-8")
            img_tr = fromstring(img_html)
            img_url = img_tr.xpath("//img/@src")[0]
            img_caption = img_tr.xpath('//p[@class="wp-caption-text"]/text()').pop()
            img_hash = self.downloader.download_image(img_url)
            img_parent = img.getparent()
            img_parent.replace(img, etree.Comment(f"#blog2epubimage#{img_hash}#"))
            self.tree = img_parent.getroottree()
            self.html = etree.tostring(self.tree).decode("utf-8")
            self.images.append(img_hash)
            self.images_captions.append(img_caption)

    def replace_images(self):
        for key, image in enumerate(self.images):
            if image:
                image_caption = ""
                if self.images_captions[key]:
                    image_caption = self.images_captions[key]
                image_html = (
                    '<table align="center" cellpadding="0" cellspacing="0" class="tr-caption-container" style="margin-left: auto; margin-right: auto; text-align: center; background: #FFF; box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5); padding: 8px;"><tbody><tr><td style="text-align: center;"><img border="0" src="images/'
                    + image
                    + '" /></td></tr><tr><td class="tr-caption" style="text-align: center;">'
                    + image_caption
                    + "</td></tr></tbody></table>"
                )
                self.html = self.html.replace("<!--#blog2epubimage#" + image + "#-->", image_html)
        self.content = self.html

    def get_content(self):
        article_header = re.findall(r"(<h1 class=\"entry-title\">[^<]*<\/h1>)", self.html)
        if article_header:
            self.html = self.html.split(article_header[0])[1]
        article_footer = re.findall(r"(<div id=\"atatags-[^\"]*\")", self.html)
        if article_footer:
            self.html = self.html.split(article_footer[0])[0]
        self.content = self.html = self.html.strip()
        self.get_tree()

    def get_tags(self):
        pass

    def process(self) -> ArticleModel:
        self.html = self._content_cleanup(self.html)
        self.tree = fromstring(self.html)
        self._content_cleanup_xpath()
        self.title = self.get_title()
        self.get_date()
        self.get_images()
        self.content = self.get_content()
        self.get_tags()
        self.get_comments()
        return ArticleModel(
            url=self.url,
            title=self.title,
            date=self.date,
            content=self.content,
            comments=self.comments,
        )
