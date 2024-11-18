import tempfile

import pytest

from blog2epub.blog2epub_main import Blog2Epub
from blog2epub.common.book import Book
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.configuration import ConfigurationModel


@pytest.fixture()
def mock_configuration() -> ConfigurationModel:
    return ConfigurationModel(
        destination_folder=tempfile.gettempdir(),
        limit="2",
    )


class TestBlog2EPubMainSalamPax:
    def test_velosov_can_parse_the_date(self, mock_configuration):
        # given
        given_blog2epub = Blog2Epub(
            url="dear_raed.blogspot.com",
            interface=EmptyInterface(),
            configuration=mock_configuration,
            cache_folder="tests_cache",
        )
        # when
        given_blog2epub.download()
        ebook = Book(
            book_data=given_blog2epub.crawler.get_book_data(),
            interface=EmptyInterface(),
            configuration=mock_configuration,
        )
        ebook.save()
        # then
        pass
