#!/usr/bin/env python3
# -*- coding : utf-8 -*-

from blog2epub.Cover import Cover

class Book(object):
    """
    Book class used in Blogspot2Epub class.
    """

    def __init__(self):
        self.cover = Cover()
        self.images = {}

    def main(self):
        pass
