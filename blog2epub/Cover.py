#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from random import shuffle

from PIL import Image, ImageDraw


class Cover(object):
    """
    Cover class used in Blog2Epub class.
    """

    def __init__(self, name, title, images=[]):
        """
        :param name: name of the book (address of the blog)
        :param title: title of the blog
        :param images: list of images
        """
        self.name = name
        self.title = title
        self.images = images

    def _make_thumb(self, img, size):
        cropped_img = self._crop_image(img, size)
        cropped_img.thumbnail(size, Image.ANTIALIAS)
        return cropped_img

    def _is_landscape(self, width, height):
        if width >= height:
            return True
        else:
            return False

    def _box_params_center(self, width, height):
        if self._is_landscape(width, height):
            upper_x = int((width / 2) - (height / 2))
            upper_y = 0
            lower_x = int((width / 2) + (height / 2))
            lower_y = height
            return upper_x, upper_y, lower_x, lower_y
        else:
            upper_x = 0
            upper_y = int((height / 2) - (width / 2))
            lower_x = width
            lower_y = int((height / 2) + (width / 2))
            return upper_x, upper_y, lower_x, lower_y

    def _crop_image(self, img, size):
        upper_x, upper_y, lower_x, lower_y = self._box_params_center(img.size[0], img.size[1])
        box = (upper_x, upper_y, lower_x, lower_y)
        region = img.crop(box)
        return region

    def generate(self):
        tile_size = 120
        tiles_count_y = 5
        tiles_count_x = 7
        cover_image = Image.new('RGB', (600, 800))
        cover_draw = ImageDraw.Draw(cover_image)
        dark_factor = 1
        if len(self.images) > 0:
            shuffle(self.images)
            i = 1
            for x in range(0, tiles_count_x):
                for y in range(0, tiles_count_y):
                    try:
                        thumb = self._make_thumb(Image.open(self.images[i - 1]), (tile_size, tile_size))
                        thumb = thumb.point(lambda p: p * dark_factor)
                        dark_factor = dark_factor - 0.03
                        cover_image.paste(thumb, (y * tile_size, x * tile_size))
                        i = i + 1
                    except Exception as e:
                        print(e)
                    if i > len(self.images):
                        i = 1
        cover_draw.text((15, 635), title, (255, 255, 255), font=ImageFont.truetype("Lato-Bold.ttf", 30))
        cover_draw.text((15, 760), sys.argv[1] + ".blogspot.com", (255, 255, 255),
                        font=ImageFont.truetype("Lato-Regular.ttf", 20))
        if START_DATE == END_DATE:
            cover_draw.text((15, 670), START_DATE, (150, 150, 150), font=ImageFont.truetype("Lato-Italic.ttf", 20))
        else:
            end_date = END_DATE.split(' ')
            start_date = START_DATE.split(' ')
            if len(end_date) == len(start_date):
                ed = []
                for i, d in enumerate(end_date):
                    if d != start_date[i]:
                        ed.append(d)
            ed = ' '.join(ed)
            cover_draw.text((15, 670), ed + " - " + START_DATE, (150, 150, 150),
                            font=ImageFont.truetype("Lato-Italic.ttf", 20))
        cover_image = cover_image.convert('L')
        cover_image.save(file_name + '.jpg', format='JPEG', quality=100)
