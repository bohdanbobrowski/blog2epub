from typing import Optional, List

from blog2epub.crawlers import AbstractCrawler
import urllib.robotparser


class UniversalCrawler(AbstractCrawler):
    """Attempt to create universal crawler, that can scrap website content similar like Firefox does prepare read-view
    basing on sitemap.xml file."""

    def _get_sitemaps(self, sitemaps_content: Optional[str] = None) -> List[str] | None:
        robot_parser = urllib.robotparser.RobotFileParser()
        robot_parser.set_url("https://starybezpiek.blogspot.com/robots.txt")
        robot_parser.read()
        return robot_parser.site_maps()

    def _get_sitemap_xml(self):
        pass

    def crawl(self):
        pass

    def generate_ebook(self, **kwargs):
        pass
