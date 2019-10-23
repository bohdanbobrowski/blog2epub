#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from tkinter import *
from tkinter.ttk import *
import sys
import os
import platform
import yaml
from pathlib import Path
from urllib import parse

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface


class TkInterface(EmptyInterface):

    def __init__(self, consoleOutput, refresh):
        self.consoleOutput = consoleOutput
        self.refresh = refresh

    def print(self, text):
        self.consoleOutput.insert(END, text + '\n')
        self.consoleOutput.see('end')
        self.refresh()

    def notify(self, title, subtitle, message, cover):
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

    def exception(self, e):
        self.consoleOutput.insert(END, str(e) + '\n')
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


class Blog2EpubGui(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)    
        self.settings = Blog2EpubSettings()             
        self.master = master
        self.consoleOutput = Text(self.master)
        self.urlEntry = Entry(self.master, width=10)
        self.setEntryValue(self.urlEntry, self.settings.get('url'))
        self.limitEntry = Entry(self.master, width=10)
        self.setEntryValue(self.limitEntry, self.settings.get('limit'))
        self.skipEntry = Entry(self.master, width=10)
        self.setEntryValue(self.skipEntry, self.settings.get('skip'))
        self.interface = TkInterface(self.consoleOutput, self.master.update)
        self.init_window()

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
    def setEntryValue(e, v=''):
        e.delete(0, END)
        e.insert(0, v)

    def init_window(self):
        self.master.title('Blog2Epub')
        # Url:
        Label(self.master, text='Url:').grid(row=0)
        self.urlEntry.grid(row=0, column=1, columnspan=2, sticky=W+E)
        # Button:
        downloadButton = Button(self.master, text='Download', command=self.download)
        downloadButton.grid(row=0, column=3)
        # Limit:
        Label(self.master, text='Limit:').grid(row=1)
        self.limitEntry.grid(row=1, column=1)
        # Skip:
        Label(self.master, text='Skip:').grid(row=1, column=2)
        self.skipEntry.grid(row=1, column=3)
        # Text
        self.consoleOutput.grid(row=2, columnspan=4)
        self.consoleOutput.config(bg='black', fg='white')

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

    def download(self):
        self.interface.clear()
        try:
            blog2epub = Blog2Epub(self._get_params())
            self.interface.print('Downloading...')
            blog2epub.download()
            self.saveSettings()
        except Exception as e:
            self.interface.exception(e)


def main():
    root = Tk()
    root.style = Style()
    # ('aqua', 'clam', 'alt', 'default', 'classic')
    # root.style.theme_use('aqua')
    # root.config(background='systemWindowBody')
    root.resizable(False, False)
    Blog2EpubGui(root)
    root.lift()
    root.call('wm', 'attributes', '.', '-topmost', '1')
    root.after_idle(root.call, 'wm', 'attributes', '.', '-topmost', False)
    root.mainloop() 