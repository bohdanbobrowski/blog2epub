import unittest
from unittest.mock import patch

from blog2epub.common.crawler import (
    prepare_url,
    prepare_file_name,
    prepare_url_to_crawl,
    prepare_port,
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

    def test_prepare_url(self):
        # When:
        result_0 = prepare_url(self.given_domain)
        result_1 = prepare_url(self.given_http_url)
        result_2 = prepare_url(self.given_https_url)
        # Then:
        assert result_0 == self.given_domain
        assert result_1 == self.given_domain
        assert result_2 == self.given_domain

    def test_prepare_url_always_subdomain_for_blogspot_and_wordpress_com(self):
        # When
        result_1 = prepare_url("https://test.blogspot.com/sub-category/name.html")
        result_2 = prepare_url(
            "https://test.wordpress.com/sub-category/very-interesting-article.html"
        )
        # Then
        assert result_1 == "test.blogspot.com"
        assert result_2 == "test.wordpress.com"

    def test_prepare_file_name(self):
        # When:
        result_1 = prepare_file_name("", self.given_domain)
        result_2 = prepare_file_name("xxx", self.given_domain)
        # Then:
        assert result_1 == "example_com"
        assert result_2 == "xxx"

    @patch("urllib.request.urlopen")
    def test_prepare_url_to_crawl(self, mock_urlopen):
        # Given
        mock_urlopen.return_value = MockRequestResult("ddd")
        # When:
        result = prepare_url_to_crawl(self.given_domain)
        # Then:
        assert mock_urlopen.called
        assert mock_urlopen.call_count == 1
        assert mock_urlopen.call_args_list[0].args == (self.given_https_url,)
        assert result == "ddd"

    def test_prepare_port(self):
        # When:
        http_result = prepare_port(self.given_http_url)
        https_result = prepare_port(self.given_https_url)
        # Then:
        assert http_result == 80
        assert https_result == 443
