 #!/usr/bin/env python3
# -*- coding : utf-8 -*-

import re
from blog2epub.crawlers.Crawler import Crawler, Article

class CrawlerNrdblog(Crawler):
    """
    Cmos NRDblog crawler.

    http://nrdblog.cmosnet.eu/nrd/zegnaj-nrd/
    
    """

    images_regex = r'<table[^>]*><tbody>[\s]*<tr><td[^>]*><a href="([^"]*)"[^>]*><img[^>]*></a></td></tr>[\s]*<tr><td class="tr-caption" style="[^"]*">([^<]*)'
    articles_regex = r'<a title="([^"]+)" href="([^"]+)">'

    def _get_articles(self, content):
        articles_list = re.findall(self.articles_regex, content)
        output = []
        for art in articles_list:
            output.append(Article(art[1], art[0], self))
        return output

    def _prepare_content(self, content):
        start = content.find('<div class="entry-content">')
        stop = content.find('</div><!-- .entry-content -->')
        if start > -1 and stop > -1:
            content = content[start:]
            content = content[:stop]
        return content

    def _get_url_to_crawl(self, tree):
        # All articles are listed in one page, there is no need to crawl
        return None