import tempfile
from unittest.mock import MagicMock, patch

import pytest

from blog2epub.common.interfaces import EmptyInterface
from blog2epub.crawlers.default import DefaultCrawler
from blog2epub.models.configuration import ConfigurationModel


@pytest.fixture()
def mock_configuration() -> ConfigurationModel:
    return ConfigurationModel(
        destination_folder=tempfile.gettempdir(),
        limit="2",
    )


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, file_name, status_code=200):
            self.file_name = file_name
            self.status_code = status_code

        @property
        def content(self):
            if self.file_name:
                with open(f"tests/unit/blog2epub/crawlers/data/{self.file_name}", "rb") as f:
                    content = f.read()
                return content
            return None

    if args and len(args) > 0:
        fname = args[0].replace("http://", "").replace("https://", "").replace("/", "_")
        if fname.find(".xml?page=") != -1:
            fname = fname.replace(".xml?page=", "") + ".xml"
        return MockResponse(fname, 200)

    return MockResponse(None, 404)


class TestDefaultCrawler:
    @patch(
        "urllib.robotparser.RobotFileParser",
        MagicMock(return_value=MagicMock(sitemaps=["https://bohdan.bobrowski.com.pl/wp-sitemap.xml"])),
    )
    def test_get_sitemap_url(self, mock_configuration):
        # Given
        with open("tests/unit/blog2epub/crawlers/data/robots-1.txt") as f:
            f.read()
        given_crawler = DefaultCrawler(
            url="bohdan.bobrowski.com.pl",
            configuration=mock_configuration,
            interface=EmptyInterface(),
        )
        # When
        result = given_crawler._get_sitemap_url()
        # Then
        assert result == "https://bohdan.bobrowski.com.pl/wp-sitemap.xml"

    @patch(
        "urllib.robotparser.RobotFileParser",
        MagicMock(return_value=MagicMock(sitemaps=["https://bohdan.bobrowski.com.pl/wp-sitemap.xml"])),
    )
    @patch("requests.get", MagicMock(side_effect=mocked_requests_get))
    def test_get_pages_urls(self, mock_configuration):
        # given
        given_crawler = DefaultCrawler(
            url="bohdan.bobrowski.com.pl",
            interface=EmptyInterface(),
            configuration=mock_configuration,
            cache_folder="tests_cache",
        )
        # when
        sitemap_url = given_crawler._get_sitemap_url()
        pages = given_crawler._get_pages_urls(sitemap_url=sitemap_url)
        # then
        assert "https://bohdan.bobrowski.com.pl/2023/01/film-kolberg-1945/" in pages
        assert "https://bohdan.bobrowski.com.pl/2023/03/wielka-ucieczka/" in pages
        assert "https://bohdan.bobrowski.com.pl/" not in pages
        assert "https://bohdan.bobrowski.com.pl/wp-sitemap-taxonomies-category-1.xml" not in pages
        assert "https://bohdan.bobrowski.com.pl/wp-sitemap-taxonomies-post_tag-1.xml" not in pages
        assert "https://bohdan.bobrowski.com.pl/wp-sitemap-users-1.xml" not in pages

    @patch(
        "urllib.robotparser.RobotFileParser",
        MagicMock(return_value=MagicMock(sitemaps=["https://rocket-garage.blogspot.com/sitemap.xml"])),
    )
    @patch("requests.get", MagicMock(side_effect=mocked_requests_get))
    def test_rocket_garage_blogspot_com(self, mock_configuration):
        # given
        given_crawler = DefaultCrawler(
            url="rocket-garage.blogspot.com",
            interface=EmptyInterface(),
            configuration=mock_configuration,
        )
        # when
        sitemap_url = given_crawler._get_sitemap_url()
        pages = given_crawler._get_pages_urls(sitemap_url=sitemap_url)
        # then
        assert len(pages) > 1000
