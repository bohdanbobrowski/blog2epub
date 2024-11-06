import unittest

from blog2epub.common.crawler import (
    prepare_port_and_url,
    prepare_file_name,
)


class MockRequestResult:
    def __init__(self, url):
        self.url = url

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return self

    def geturl(self):
        return self.url


class TestCommonCrawler(unittest.TestCase):
    def setUp(self):
        # Given:
        self.given_domain = "example.com"
        self.given_http_url = "http://example.com"
        self.given_https_url = "https://example.com"

    def test_prepare_port_and_url(self):
        # When:
        port_0, result_0 = prepare_port_and_url(self.given_domain)
        port_1, result_1 = prepare_port_and_url(self.given_http_url)
        port_2, result_2 = prepare_port_and_url(self.given_https_url)
        # Then:
        assert result_0 == self.given_https_url
        assert result_1 == self.given_http_url
        assert result_2 == self.given_https_url
        assert port_0 == 443
        assert port_1 == 80
        assert port_2 == 443

    def test_prepare_url_always_subdomain_for_blogspot_and_wordpress_com(self):
        # When
        port_0, result_1 = prepare_port_and_url(
            "https://test.blogspot.com/sub-category/name.html"
        )
        port_1, result_2 = prepare_port_and_url(
            "https://test.wordpress.com/sub-category/very-interesting-article.html"
        )
        # Then
        assert result_1 == "https://test.blogspot.com"
        assert result_2 == "https://test.wordpress.com"

    def test_prepare_file_name(self):
        # When:
        result_1 = prepare_file_name("", self.given_domain)
        result_2 = prepare_file_name("xxx", self.given_domain)
        # Then:
        assert result_1 == "example_com"
        assert result_2 == "xxx"
