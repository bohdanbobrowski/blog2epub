import tempfile

import pytest
from blog2epub.blog2epub_main import Blog2Epub
from blog2epub.models.configuration import ConfigurationModel


@pytest.fixture()
def mock_configuration() -> ConfigurationModel:
    return ConfigurationModel(
        destination_folder=tempfile.gettempdir(),
        limit="1",
    )


class TestBlog2EPubMain:
    def test_starybezpiek_downloads_one_article(self, mock_configuration):
        # given
        given_blog2epub = Blog2Epub(
            url="starybezpiek.blogspot.com",
            configuration=mock_configuration,
        )
        # when
        given_blog2epub.download()
        # then
        assert len(given_blog2epub.crawler.articles) == 1
        assert len(given_blog2epub.crawler.images) > 1
