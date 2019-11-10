 #!/usr/bin/env python3
# -*- coding : utf-8 -*-

import re
from blog2epub.crawlers.Crawler import Crawler, Article
from pocket import Pocket, PocketException

class CrawlerPocket(Crawler):
    """
    https://getpocket.com
    
	87372-bc12512b803ed33d9c1c56e0
    """

    def __init__(self, url, include_images=True, images_height=800, images_width=600, images_quality=40, start=None,
                 end=None, limit=None, skip=False, force_download=False, file_name=None, destination_folder='./',
                 cache_folder=None, language=None, interface=None):
        Crawler.__init__(url, include_images, images_height, images_width, images_quality, start, end, limit, skip, force_download,
        file_name, destination_folder, cache_folder, language, interface)
        self.pocket = Pocket(consumer_key='87372-bc12512b803ed33d9c1c56e0', access_token='<Your Access Token>')

    def _crawl():
        print(p.retrieve(offset=0, count=10))