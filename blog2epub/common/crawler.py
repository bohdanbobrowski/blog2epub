from urllib import request


def prepare_url(url: str) -> str:
    return url.replace("http:", "").replace("https:", "").strip("/")


def prepare_file_name(file_name: str | None, url: str) -> str:
    if file_name:
        return file_name
    return url.replace("/", "_")


def prepare_url_to_crawl(url: str) -> str:
    with request.urlopen("https://" + url) as r:
        response = r.geturl()
    return response


def prepare_port(url):
    if url.startswith("https://"):
        return 443
    return 80
