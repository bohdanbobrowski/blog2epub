import os.path
import tempfile

import pytest
from blog2epub.blog2epub_main import Blog2Epub
from blog2epub.models.configuration import ConfigurationModel
from blog2epub.common.book import Book


@pytest.fixture()
def mock_configuration() -> ConfigurationModel:
    return ConfigurationModel(
        destination_folder=tempfile.gettempdir(),
        limit="2",
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
        ebook = Book(
            book_data=given_blog2epub.crawler.get_book_data(),
            configuration=mock_configuration,
        )
        ebook.save()
        # then
        assert len(given_blog2epub.crawler.articles) == 2
        assert len(given_blog2epub.crawler.images) > 1
        assert ebook.file_name == "starybezpiek_blogspot_com_2015.09.23-2015.12.15.epub"
        assert os.path.isfile("./starybezpiek_blogspot_com_2015.09.23-2015.12.15.epub")
        assert os.path.isfile(ebook.cover_image_path)
