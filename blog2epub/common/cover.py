import os
import platform
from random import shuffle
from typing import List

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from blog2epub.common.assets import asset_path
from blog2epub.common.globals import VERSION
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.models.book import DirModel, ImageModel

TITLE_FONT_NAME = asset_path("Alegreya-Regular.ttf")
SUBTITLE_FONT_NAME = asset_path("Alegreya-Italic.ttf")
GENERATOR_FONT_NAME = asset_path("MartianMono-Regular.ttf")


class Cover:
    """
    Cover class used in Blog2Epub class.
    """

    tile_size = 120

    def __init__(
        self,
        dirs: DirModel,
        interface: EmptyInterface,
        file_name: str,
        blog_url: str,
        title: str,
        subtitle: str,
        images: List[ImageModel],
        platform_name: str = "",
    ):
        """
        :param book: intance of Book class
        """
        self.dirs = dirs
        self.interface = interface
        self.file_name = file_name
        self.blog_url = blog_url
        self.title = title
        self.subtitle = subtitle
        self.images = self._check_image_size(set(i.hash for i in images))
        self.platform_name = platform_name

    def _check_image_size(self, image_hashes: set[str]):
        verified_images = []
        for image_hash in image_hashes:
            if image_hash:
                img_file = os.path.join(self.dirs.images, image_hash)
                if os.path.isfile(img_file):
                    img = Image.open(img_file)
                    if img.size[0] >= self.tile_size and img.size[1] >= self.tile_size:
                        verified_images.append(image_hash)
        return verified_images

    def _make_thumb(self, img, size):
        cropped_img = self._crop_image(img)
        cropped_img.thumbnail(size, Image.LANCZOS)
        return cropped_img

    def _is_landscape(self, width, height):
        if width >= height:
            return True
        return False

    def _box_params_center(self, width, height):
        if self._is_landscape(width, height):
            upper_x = int((width / 2) - (height / 2))
            upper_y = 0
            lower_x = int((width / 2) + (height / 2))
            lower_y = height
            return upper_x, upper_y, lower_x, lower_y
        upper_x = 0
        upper_y = int((height / 2) - (width / 2))
        lower_x = width
        lower_y = int((height / 2) + (width / 2))
        return upper_x, upper_y, lower_x, lower_y

    def _crop_image(self, img):
        upper_x, upper_y, lower_x, lower_y = self._box_params_center(
            img.size[0], img.size[1]
        )
        box = (upper_x, upper_y, lower_x, lower_y)
        region = img.crop(box)
        return region

    def _draw_text(self, cover_image):
        cover_draw = ImageDraw.Draw(cover_image)
        title_font = ImageFont.truetype(TITLE_FONT_NAME, 30)
        subtitle_font = ImageFont.truetype(SUBTITLE_FONT_NAME, 20)
        generator_font = ImageFont.truetype(GENERATOR_FONT_NAME, 10)
        title_length = title_font.getlength(self.title)
        if title_length <= 570:
            cover_draw.text(
                (15, 635),
                self.title,
                (255, 255, 255),
                font=title_font,
            )
        else:
            title = self.title.split(" - ")
            buffer = 35 * (len(title) - 1)
            title = "\n".join(title)
            cover_draw.text(
                (15, 635 - buffer),
                title,
                (255, 255, 255),
                font=title_font,
            )
        cover_draw.text(
            (15, 670),
            self.subtitle,
            (150, 150, 150),
            font=subtitle_font,
        )
        cover_draw.text(
            (15, 750),
            f"Generated with blog2epub v{VERSION} {self.platform_name}\nfrom {self.blog_url}",
            (155, 155, 155),
            font=generator_font,
        )
        return cover_image

    def generate(self):
        tiles_count_y = 5
        tiles_count_x = 7
        cover_image = Image.new("RGB", (600, 800))
        self.interface.print(
            f"Generating cover (800px*600px) from {len(self.images)} images."
        )
        dark_factor = 1.0
        if len(self.images) > 0:
            if len(self.images) > 1:
                shuffle(self.images)
            i = 1
            for x in range(0, tiles_count_x):
                if len(self.images) > 1 & len(self.images) <= tiles_count_y * 2:
                    shuffle(self.images)
                for y in range(0, tiles_count_y):
                    img_file = os.path.join(self.dirs.images, self.images[i - 1])
                    thumb = self._make_thumb(
                        Image.open(img_file), (self.tile_size, self.tile_size)
                    )
                    enhancer = ImageEnhance.Brightness(thumb)
                    thumb = enhancer.enhance(dark_factor)
                    dark_factor -= 0.03
                    cover_image.paste(thumb, (y * self.tile_size, x * self.tile_size))
                    i = i + 1
                    if i > len(self.images):
                        i = 1
        cover_image = self._draw_text(cover_image)
        cover_image = cover_image.convert("L")
        cover_file_name = self.file_name + ".jpg"
        cover_file_full_path = os.path.join(self.dirs.path, cover_file_name)
        cover_image.save(cover_file_full_path, format="JPEG", quality=100)
        self.interface.print(
            f"Cover generated: {cover_file_full_path}"
        )
        return cover_file_name, cover_file_full_path
