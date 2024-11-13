import tempfile

import pytest

from blog2epub.common.interfaces import EmptyInterface
from blog2epub.crawlers import DefaultCrawler
from blog2epub.models.configuration import ConfigurationModel


@pytest.fixture()
def mock_configuration() -> ConfigurationModel:
    return ConfigurationModel(
        destination_folder=tempfile.gettempdir(),
        limit="1",
    )


class TestDefaultCrawler:
    # TODO: change this tests to unit test

    def test_get_sitemap_url(self, mock_configuration):
        # given
        given_crawler = DefaultCrawler(
            url="bohdan.bobrowski.com.pl",
            interface=EmptyInterface(),
            configuration=mock_configuration,
            cache_folder="tests_cache",
        )
        # when
        sitemap_url = given_crawler._get_sitemap_url()
        # then
        assert sitemap_url == "https://bohdan.bobrowski.com.pl/wp-sitemap.xml"

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
