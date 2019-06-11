#!/usr/bin/env python
# -*- coding: utf-8 -*-
# blogspot2epub
# version 0.2
# author: Bohdan Bobrowski bohdan@bobrowski.com.pl

import os
import re
import sys
import hashlib
from ebooklib import epub
from datetime import datetime
from lxml import html
from lxml import etree
from os import listdir
from os.path import isfile, join
from BeautifulSoup import BeautifulStoneSoup


def HTMLEntitiesToUnicode(text):
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text




