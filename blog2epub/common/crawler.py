from urllib import request
import ssl
from urllib.error import URLError

from blog2epub.common.exceptions import BadUrlException

ssl._create_default_https_context = ssl._create_stdlib_context  # type: ignore


def prepare_url(url: str) -> str:
    return url.replace("http:", "").replace("https:", "").strip("/")


def prepare_file_name(file_name: str | None, url: str) -> str:
    if file_name:
        return file_name
    return url.replace("/", "_")


def prepare_url_to_crawl(url: str) -> str:
    try:
        with request.urlopen("https://" + url) as r:
            return r.geturl()
    except URLError:
        raise BadUrlException


def prepare_port(url):
    if url.startswith("https://"):
        return 443
    return 80
