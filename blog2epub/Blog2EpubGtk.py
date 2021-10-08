#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import gi
import sys
import os
import platform
import yaml
import subprocess
from pathlib import Path
from urllib import parse

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

VERSION = '1.1.0'

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Blog2Epub")        
        self.settings = Blog2EpubSettings()
        # Layout
        # self.set_default_size(500, 400)
        self.set_resizable(False) 
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(5)
        self.grid.set_column_spacing(5)
        # Input
        text_label = Gtk.Label(label="Url:")
        self.grid.add(text_label)
        self.text = Gtk.Entry()
        self.text.set_activates_default(True)
        self.grid.attach_next_to(self.text, text_label, Gtk.PositionType.RIGHT, 3, 1)
        # Text output
        self.textview = Gtk.TextView()
        self.textview.set_monospace(True)
        self.textview.set_size_request(500,500)
        self.textview.show()
        self.textbuffer = self.textview.get_buffer()
        self.grid.attach_next_to(self.textview, text_label, Gtk.PositionType.BOTTOM, 4, 4)
        # About button
        self.about_button = Gtk.Button(label="About")
        self.about_button.connect("clicked", self.about)
        self.grid.attach_next_to(self.about_button, self.textview, Gtk.PositionType.BOTTOM, 1, 1)
        self.add(self.grid)
        # Download button
        self.download_button = Gtk.Button(label="Download")
        self.download_button.connect("clicked", self.download)
        self.grid.attach_next_to(self.download_button, self.about_button, Gtk.PositionType.RIGHT, 1, 1)
        # self.add(self.grid)

    def print(self, text):
        self.textbuffer.insert(text + '\n')
        self.textbuffer.see('end')

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
        if parse.urlparse(self.urlEntry.get()):
            return self.urlEntry.get()
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
            'limit': self._is_int(self.limitEntry.get()),
            'skip': self._is_int(self.skipEntry.get()),
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
        self.settings.set('url', self.urlEntry.get())
        self.settings.set('limit', self.limitEntry.get())
        self.settings.set('skip', self.skipEntry.get())
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
        about = Gtk.AboutDialog()
        about.set_program_name("Blog2Epub")
        about.set_version(VERSION)
        about.set_comments("Nifty script to convert blog into ebook.")
        about.set_website("https://github.com/bohdanbobrowski/blogspot2epub")
        about.run()
        about.destroy()


class TkInterface(EmptyInterface):

    def __init__(self, consoleOutput, refresh):
        self.consoleOutput = consoleOutput
        self.refresh = refresh

    def print(self, text):
        self.consoleOutput.insert(END, text + '\n')
        self.consoleOutput.see('end')
        self.refresh()

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
        print("Exception: " + str(e))
        self.consoleOutput.insert(END, "Exception: " + str(e) + '\n')
        self.consoleOutput.see('end')
        self.refresh()            

    def clear(self):
        self.consoleOutput.delete(1.0, END)


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
