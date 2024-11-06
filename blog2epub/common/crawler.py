from typing import Tuple
from urllib import parse
import ssl


ssl._create_default_https_context = ssl._create_stdlib_context  # type: ignore


def prepare_port_and_url(url: str) -> Tuple[int, str]:
    default_port = 80
    if not url.startswith("http"):
        url = "https://" + url
    if not url.startswith("http://"):
        default_port = 443
    port = parse.urlparse(url).port
    scheme = parse.urlparse(url).scheme
    hostname = parse.urlparse(url).hostname
    return port or default_port, f"{scheme}://{hostname}"


def prepare_file_name(file_name: str | None, url: str) -> str:
    # TODO: refactor this!
    if file_name:
        return file_name
    result = url.lower()
    result = result.replace("http://", "")
    result = result.replace("https://", "")
    for x in ["/", ",", "."]:
        result = result.replace(x, "_")
    return result
