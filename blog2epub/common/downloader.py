import gzip
import hashlib
import os
import re
import time
from typing import Mapping, Optional
from urllib.parse import urlparse

import filetype  # type: ignore
import requests
from imagesize import imagesize  # type: ignore
from PIL import Image
from requests.cookies import RequestsCookieJar

from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import DirModel, ImageModel


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
        interface: EmptyInterface,
        images_size: list[int],
        images_quality: int,
        ignore_downloads: list[str],
    ):
        self.dirs = dirs
        self.url = url
        self.interface = interface
        self.images_size = images_size
        self.images_quality = images_quality
        self.ignore_downloads = ignore_downloads
        self.cookies = RequestsCookieJar()
        self.session = requests.session()
        self.headers: Mapping[str, str] = {}
        self.skipped_images: list[str] = []

    def get_urlhash(self, url):
        m = hashlib.md5()
        m.update(url.encode("utf-8"))
        return m.hexdigest()

    def file_write(self, contents: bytes, filepath: str):
        filepath = filepath + ".gz"
        with gzip.open(filepath, "wb") as f:
            f.write(contents)

    def file_read(self, filepath: str) -> bytes:
        if os.path.isfile(filepath + ".gz"):
            with gzip.open(filepath + ".gz", "rb") as f:
                contents = f.read()
        else:
            with open(filepath, "rb") as html_file:
                contents = html_file.read()
            self.file_write(contents, filepath)
            os.remove(filepath)
        return contents

    def get_filepath(self, url: str) -> str:
        return os.path.join(self.dirs.html, self.get_urlhash(url) + ".html")

    def _is_url_in_ignored(self, url: str) -> bool:
        for search_rule in self.ignore_downloads:
            if re.match(search_rule, url):
                return True
        return False

    def _is_url_in_skipped(self, url: str) -> bool:
        if url in self.skipped_images:
            return True
        return False

    def file_download(self, url: str, filepath: str) -> Optional[bytes]:
        if self._is_url_in_ignored(url) or self._is_url_in_skipped(url):
            return None
        prepare_directories(self.dirs)
        try:
            response = self.session.get(url, cookies=self.cookies, headers=self.headers)
        except requests.exceptions.ConnectionError:
            return None
        self.cookies = response.cookies
        self.file_write(response.content, filepath)
        return response.content

    @staticmethod
    def check_interstitial(contents: bytes | str):
        if isinstance(contents, bytes):
            contents = contents.decode("utf-8")
        interstitial = re.findall('interstitial=([^"]+)', contents)
        if interstitial:
            return interstitial[0]
        return False

    def get_content(self, url) -> Optional[bytes]:
        # TODO: This needs refactor!
        filepath = self.get_filepath(url)
        contents = None
        for _x in range(0, 3):
            if not os.path.isfile(filepath) and not os.path.isfile(filepath + ".gz"):
                contents = self.file_download(url, filepath)
            else:
                contents = self.file_read(filepath)
            if contents is not None:
                break
            self.interface.print(f"...repeat request: {url}")
            time.sleep(3)
        if contents is not None:
            interstitial = self.check_interstitial(contents)
            if interstitial:
                interstitial_url = "http://" + self.url + "?interstitial=" + interstitial
                self.file_download(interstitial_url, self.get_filepath(interstitial_url))
                contents = self.file_download(
                    "http://" + self.url,
                    self.get_filepath("http://" + self.url),
                )
        return contents

    def _fix_image_url(self, img: str) -> str:
        if not img.startswith("http"):
            uri = urlparse(self.url)
            if uri.netloc not in img:
                img = os.path.join(uri.netloc, img)
            while not img.startswith("//"):
                img = "/" + img
            img = f"{uri.scheme}:{img}"
        return img

    def _download_image(self, url: str, filepath: str) -> Optional[bool]:
        if self._is_url_in_ignored(url) or self._is_url_in_skipped(url):
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

    def download_image(self, image_obj: ImageModel) -> bool:
        if self._is_url_in_ignored(image_obj.url) or self._is_url_in_skipped(image_obj.url):
            return False
        image_obj.url = self._fix_image_url(image_obj.url)
        img_hash = self.get_urlhash(image_obj.url)
        img_type = os.path.splitext(image_obj.url)[1].lower()
        if img_type not in [".jpeg", ".jpg", ".png", ".bmp", ".gif", ".webp"]:
            return False
        original_fn = os.path.join(self.dirs.originals, img_hash + "." + img_type)
        resized_fn = os.path.join(self.dirs.images, img_hash + ".jpg")
        if os.path.isfile(resized_fn):
            return True
        if not os.path.isfile(resized_fn):
            self._download_image(image_obj.url, original_fn)
        if os.path.isfile(original_fn):
            original_img_type = filetype.guess(original_fn)
            if original_img_type is None:
                return False
            if not original_img_type.MIME.startswith("image"):
                os.remove(original_fn)
                self.skipped_images.append(image_obj.url)
                return False
            image_size = imagesize.get(original_fn)
            if image_size[0] + image_size[1] < 100:
                os.remove(original_fn)
                self.skipped_images.append(image_obj.url)
                return False
            picture = Image.open(original_fn)
            if picture.size[0] > self.images_size[0] or picture.size[1] > self.images_size[1]:
                picture.thumbnail(self.images_size, Image.LANCZOS)  # type: ignore
            converted_picture = picture.convert("L")
            converted_picture.save(resized_fn, format="JPEG", quality=self.images_quality)
            os.remove(original_fn)
            return True
        return False
