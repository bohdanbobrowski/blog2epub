import ssl
from urllib import parse

ssl._create_default_https_context = ssl._create_stdlib_context  # type: ignore


def prepare_port_and_url(url: str) -> tuple[int, str]:
    url = url.strip()
    url = url.replace(" ", "")
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


def clever_decode(input: bytes) -> str:
    """It's not clever at all."""
    try:
        return input.decode("utf-8")
    except UnicodeDecodeError:
        return input.decode("latin-1")
