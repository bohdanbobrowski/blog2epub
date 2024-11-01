import gzip
import hashlib
import imghdr
import os
import re

from typing import Optional, List, Mapping
from urllib.parse import urlparse
import time
from PIL import Image

import requests
from requests.cookies import RequestsCookieJar

from blog2epub.models.book import DirModel
from blog2epub.common.interfaces import EmptyInterface


def prepare_directories(dirs: DirModel):
    paths = [dirs.html, dirs.images, dirs.originals]
    for p in paths:
        if not os.path.exists(p):
            os.makedirs(p)


class Downloader:
    def __init__(
        self,
        dirs: DirModel,
        url: str,
        url_to_crawl: str,
        interface: EmptyInterface,
        images_size: List[int],
        images_quality: int,
        ignore_downloads: List[str],
    ):
        self.dirs = dirs
        self.url = url
        self.url_to_crawl = url_to_crawl
        self.interface = interface
        self.images_size = images_size
        self.images_quality = images_quality
        self.ignore_downloads = ignore_downloads
        self.cookies = RequestsCookieJar()
        self.session = requests.session()
        self.headers: Mapping[str, str] = {}

    def get_urlhash(self, url):
        m = hashlib.md5()
        m.update(url.encode("utf-8"))
        return m.hexdigest()

    def file_write(self, contents, filepath):
        filepath = filepath + ".gz"
        with gzip.open(filepath, "wb") as f:
            f.write(contents.encode("utf-8"))

    def file_read(self, filepath):
        if os.path.isfile(filepath + ".gz"):
            with gzip.open(filepath + ".gz", "rb") as f:
                contents = f.read().decode("utf-8")
        else:
            with open(filepath, "rb") as html_file:
                contents = html_file.read().decode("utf-8")
            self.file_write(contents, filepath)
            os.remove(filepath)
        return contents

    def get_filepath(self, url):
        return os.path.join(self.dirs.html, self.get_urlhash(url) + ".html")

    def _is_url_in_ignored(self, url) -> bool:
        for search_rule in self.ignore_downloads:
            if re.match(search_rule, url):
                return True
        return False

    def file_download(self, url: str, filepath: str) -> Optional[str]:
        if self._is_url_in_ignored(url):
            return None
        prepare_directories(self.dirs)
        try:
            response = self.session.get(url, cookies=self.cookies, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return None
        self.cookies = response.cookies
        data = response.content
        contents = data.decode("utf-8")
        self.file_write(contents, filepath)
        return contents

    def image_download(self, url: str, filepath: str) -> Optional[bool]:
        if self._is_url_in_ignored(url):
            return None
        prepare_directories(self.dirs)
        try:
            response = self.session.get(url, cookies=self.cookies, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return False
        with open(filepath, "wb") as f:
            f.write(response.content)
        time.sleep(1)
        return True

    def checkInterstitial(self, contents):
        interstitial = re.findall('interstitial=([^"]+)', contents)
        if interstitial:
            return interstitial[0]
        return False

    def get_content(self, url):
        # TODO: This needs refactor!
        filepath = self.get_filepath(url)
        for x in range(0, 3):
            if not os.path.isfile(filepath) and not os.path.isfile(filepath + ".gz"):
                contents = self.file_download(url, filepath)
            else:
                contents = self.file_read(filepath)
            if contents is not None:
                break
            self.interface.print(f"...repeat request: {url}")
            time.sleep(3)
        if contents is not None:
            interstitial = self.checkInterstitial(contents)
            if interstitial:
                interstitial_url = (
                    "http://" + self.url + "?interstitial=" + interstitial
                )
                self.file_download(
                    interstitial_url, self.get_filepath(interstitial_url)
                )
                contents = self.file_download(
                    "http://" + self.url,
                    self.get_filepath("http://" + self.url),
                )
        return contents

    def _fix_image_url(self, img: str) -> str:
        if not img.startswith("http"):
            uri = urlparse(self.url_to_crawl)
            if uri.netloc not in img:
                img = os.path.join(uri.netloc, img)
            while not img.startswith("//"):
                img = "/" + img
            img = f"{uri.scheme}:{img}"
        return img

    def download_image(self, img: str) -> Optional[str]:
        img = self._fix_image_url(img)
        img_hash = self.get_urlhash(img)
        img_type = os.path.splitext(img)[1].lower()
        if img_type not in [".jpeg", ".jpg", ".png", ".bmp", ".gif", ".webp"]:
            return None
        original_fn = os.path.join(self.dirs.originals, img_hash + "." + img_type)
        resized_fn = os.path.join(self.dirs.images, img_hash + ".jpg")
        if os.path.isfile(resized_fn):
            return img_hash + ".jpg"
        if not os.path.isfile(resized_fn):
            self.image_download(img, original_fn)
        if os.path.isfile(original_fn):
            original_img_type = imghdr.what(original_fn)
            if original_img_type is None:
                os.remove(original_fn)
                return None
            picture = Image.open(original_fn)
            if (
                picture.size[0] > self.images_size[0]
                or picture.size[1] > self.images_size[1]
            ):
                picture.thumbnail(self.images_size, Image.LANCZOS)  # type: ignore
            converted_picture = picture.convert("L")
            converted_picture.save(
                resized_fn, format="JPEG", quality=self.images_quality
            )
            os.remove(original_fn)
            return img_hash + ".jpg"
        return None
