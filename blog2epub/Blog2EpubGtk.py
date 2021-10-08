#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import gi
import sys
import os
import platform
import yaml
import subprocess
import pathlib
import logging
from pathlib import Path
from urllib import parse
from datetime import datetime

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Pango

now = datetime.now()
date_time = now.strftime("%Y-%m-%d[%H.%M.%S]")
logging_filename = os.path.join(str(Path.home()), '.blog2epub', 'blog2epub_{}.log'.format(date_time))

logging.basicConfig(
    filename=logging_filename,
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
VERSION = '1.1.0'


class Blog2EpubTextView(Gtk.TextView):
  def __init__(self):
    Gtk.TextView.__init__(self)
    self.modify_font(
        Pango.font_description_from_string('Inconsolata 9')
    )
    text_buffer = self.get_buffer()    
    self.text_mark_end = text_buffer.create_mark("", text_buffer.get_end_iter(), False)
    self.set_monospace(True)
    self.place_cursor_onscreen()
    self.set_editable(False)
    self.set_size_request(600,600)
    self.set_cursor_visible(True) 
    self.set_hexpand(False)
    self.set_vexpand(False)    

  def append_text(self, text):
    text_buffer = self.get_buffer()
    text_iter_end = text_buffer.get_end_iter()
    text_buffer.insert(text_iter_end, text)
    self.scroll_to_mark(self.text_mark_end, 0, False, 0, 0)

  def set_text(self, text):
    text_buffer = self.get_buffer()
    text_buffer.set_text(text)


def get_image_file(filename):    
    in_binaries = os.path.join(os.path.dirname(sys.executable), filename)
    in_sources = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'images', filename)
    if os.path.isfile(in_binaries):
        return in_binaries
    if os.path.isfile(in_sources):
        return in_sources
    return False


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Blog2Epub")                
        icon_file = get_image_file('blog2epub.svg')
        if icon_file:            
            self.set_icon_from_file(icon_file)
        self.settings = Blog2EpubSettings()
        # Layout
        self.set_resizable(False) 
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(5)
        self.grid.set_column_spacing(5)
        # Url entry
        self.url_entry_label = Gtk.Label(label="Url:")
        self.grid.add(self.url_entry_label)
        self.url_entry = Gtk.Entry()
        self.url_entry.set_margin_top(5)
        self.url_entry.set_text(self.settings.get('url'))
        self.url_entry.set_activates_default(True)
        self.grid.attach_next_to(self.url_entry, self.url_entry_label, Gtk.PositionType.RIGHT, 3, 1)        
        # Download button
        self.download_button = Gtk.Button(label="Download")
        self.download_button.set_margin_top(5)
        self.download_button.connect("clicked", self.download)
        self.grid.attach_next_to(self.download_button, self.url_entry, Gtk.PositionType.RIGHT, 1, 1)
        # About button
        self.about_button = Gtk.Button(label="About")
        self.about_button.set_margin_top(5)
        self.about_button.connect("clicked", self.about)
        self.grid.attach_next_to(self.about_button, self.download_button, Gtk.PositionType.BOTTOM, 1, 1)
        self.add(self.grid)
        # Limit
        self.limit_entry_label = Gtk.Label(label="Limit:")
        self.grid.attach_next_to(self.limit_entry_label, self.url_entry_label, Gtk.PositionType.BOTTOM, 1, 1)
        self.limit_entry = Gtk.Entry()
        self.limit_entry.set_margin_top(5)
        self.limit_entry.set_text(self.settings.get('limit'))
        self.limit_entry.set_activates_default(True)
        self.grid.attach_next_to(self.limit_entry, self.limit_entry_label, Gtk.PositionType.RIGHT, 1, 1)
        # Skip
        self.skip_entry_label = Gtk.Label(label="Skip:")
        self.grid.attach_next_to(self.skip_entry_label, self.limit_entry, Gtk.PositionType.RIGHT, 1, 1)
        self.skip_entry = Gtk.Entry()
        self.skip_entry.set_margin_top(5)
        self.skip_entry.set_text(self.settings.get('skip'))
        self.skip_entry.set_activates_default(True)
        self.grid.attach_next_to(self.skip_entry, self.skip_entry_label, Gtk.PositionType.RIGHT, 1, 1)
        # Text output
        self.console_output = Blog2EpubTextView()
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(False)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.set_min_content_width(600)
        scrolledwindow.set_min_content_height(300)
        scrolledwindow.add(self.console_output)
        self.grid.attach_next_to(scrolledwindow, self.limit_entry_label, Gtk.PositionType.BOTTOM, 6, 4)
        self.interface = GtkInterface(self.console_output)

    def notify(self, title, subtitle, message, cover):
        if(platform.system() == "Darwin"):
            command = [
                'terminal-notifier',
                '-title {!r}'.format(title),
                '-subtitle {!r}'.format(subtitle),
                '-message {!r}'.format(message),
                '-contentImage {!r}'.format(cover),
                '-sound chime',
                '-appIcon {!r}'.format(os.path.join(os.path.dirname(sys.executable), 'blogspot.png')),
                '-open file:{!r}'.format(message),
            ]
            os.system('terminal-notifier {}'.format(' '.join(command)))            
        if(platform.system() == "Linux"):
            subprocess.Popen(['notify-send', subtitle + ': ' + message])

    def _get_url(self):
        if parse.urlparse(self.url_entry.get_text()):
            return self.url_entry.get_text()            
        raise Exception('Blog url is not valid.')        

    def _get_params(self):
        return {
            'interface': self.interface,
            'url': self._get_url(),
            'include_images': True,
            'images_height': 800,
            'images_width': 600,
            'images_quality': 40,
            'start': None,
            'end': None,
            'limit': self._is_int(self.limit_entry.get_text()),
            'skip': self._is_int(self.skip_entry.get_text()),
            'force_download': False,
            'file_name': None,
            'cache_folder': os.path.join(str(Path.home()), '.blog2epub'),
            'destination_folder': str(Path.home()),
        }

    @staticmethod
    def _is_int(value):
        try:
            int(value)
            return int(value)
        except:
            return None

    def saveSettings(self):
        self.settings.set('url', self.url_entry.get_text())
        self.settings.set('limit', self.limit_entry.get_text())
        self.settings.set('skip', self.skip_entry.get_text())
        self.settings.save()

    def download(self, click):
        self.interface.clear()
        try:
            self.saveSettings()
            blog2epub = Blog2Epub(self._get_params())
            self.interface.print('Downloading...')
            blog2epub.download()
        except Exception as e:
            self.interface.exception(e) 

    def about(self, click):
        logo_path = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'images', 'blog2epub.png')
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, -1, 256, True)
        about = Gtk.AboutDialog()
        about.set_program_name("Blog2Epub")
        about.set_version(VERSION)
        about.set_logo(pixbuf)
        about.set_comments("Nifty script to convert blog into ebook.")
        about.set_website("https://github.com/bohdanbobrowski/blogspot2epub")
        about.run()
        about.destroy()


class GtkInterface(EmptyInterface):
    def __init__(self, console):
        self.console = console

    def print(self, text):
        logging.info(text)
        self.console.append_text(text + "\n")
        self.gtk_update()

    def notify(self, title, subtitle, message, cover):
        if(platform.system() == "Darwin"):
            command = [
                'terminal-notifier',
                '-title {!r}'.format(title),
                '-subtitle {!r}'.format(subtitle),
                '-message {!r}'.format(message),
                '-contentImage {!r}'.format(cover),
                '-sound chime',
                '-appIcon {!r}'.format(os.path.join(os.path.dirname(sys.executable), 'blogspot.png')),
                '-open file:{!r}'.format(message),
            ]
            os.system('terminal-notifier {}'.format(' '.join(command)))            
        if(platform.system() == "Linux"):
            subprocess.Popen(['notify-send', subtitle + ': ' + message])

    def exception(self, e):
        logging.error("Exception: " + str(e))
        self.print("Exception: " + str(e))        

    def clear(self):
        self.console.set_text("")
        self.gtk_update()

    def gtk_update(self):
        while Gtk.events_pending():
            Gtk.main_iteration()
        

class Blog2EpubSettings(object):
    def __init__(self):
        self.path = os.path.join(str(Path.home()), '.blog2epub')
        self._prepare_path()
        self.fname = os.path.join(self.path, 'blog2epub.yml')
        self._data = self._read()

    def _prepare_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)        

    def _read(self):
        if not os.path.isfile(self.fname):
            self._data = self._get_default()
            self.save()
        with open(self.fname, 'rb') as stream:
            data_in_file = yaml.safe_load(stream)
            data = self._get_default()
            for k, v in data.items():
                if k in data_in_file:
                    data[k] = data_in_file[k]
        return data

    def _get_default(self):
        return {
            'url': '',
            'limit': '',
            'skip': ''
        }

    def save(self):        
        with open(self.fname, 'w') as outfile:
            yaml.dump(self._data, outfile, default_flow_style=False)

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        if key in self._data:
            return self._data[key]
        else:
            return None


def main():
    win = MyWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
