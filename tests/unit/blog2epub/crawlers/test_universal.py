import unittest

# import pytest
from blog2epub.crawlers import UniversalCrawler


class TestUniversalCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = UniversalCrawler()

    def test_robots(self):
        # Given
        # with open("tests/unit/blog2epub/crawlers/data/robots-1.txt") as f:
        #     given_robots = f.read()
        sitemaps = self.crawler._get_sitemaps()
        # When
        # Then
        print(sitemaps)

    def test_sitemap_1(self):
        # Given
        # with open("tests/unit/blog2epub/crawlers/data/sitemap-1.xml") as f:
        #     given_sitemap = f.read()
        # When
        # Then
        # print(given_sitemap)
        pass

    def test_sitemap_2(self):
        # Given
        # with open("tests/unit/blog2epub/crawlers/data/sitemap-2.xml") as f:
        #     given_sitemap = f.read()
        # # When
        # Then
        # print(given_sitemap)
        pass
