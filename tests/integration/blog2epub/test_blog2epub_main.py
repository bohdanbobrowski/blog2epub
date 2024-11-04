import tempfile

import pytest
import unittest
from blog2epub.blog2epub_main import Blog2Epub
from blog2epub.models.configuration import ConfigurationModel


@pytest.fixture()
def mock_configuration() -> ConfigurationModel:
    return ConfigurationModel(
        destination_folder=tempfile.gettempdir(),
        limit=1,
    )


class TestBlog2EPubMain(unittest.TestCase):
    def test_download(self, mock_configuration):
        # given
        given_blog2epub = Blog2Epub(
            url="https://starybezpiek.blogspot.com",
            configuration=mock_configuration,

        )
        # when
        given_blog2epub.download()
        # then
        assert True
