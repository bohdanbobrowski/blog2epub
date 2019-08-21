#!/usr/bin/env python3
# -*- coding : utf-8 -*-
from tkinter import *
from tkinter.ttk import *
import sys
import os
import platform
# if platform.system() == 'Darwin':
from pathlib import Path

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface
from urllib import parse


class TkInterface(EmptyInterface):

    def __init__(self, consoleOutput, refresh):
        self.consoleOutput = consoleOutput
        self.refresh = refresh

    def print(self, text):
        self.consoleOutput.insert(END, text + '\n')
        self.consoleOutput.see('end')
        self.refresh()

    def exception(self, e):
        self.consoleOutput.insert(END, e + '\n')
        self.consoleOutput.see('end')
        self.refresh()

    def clear(self):
        self.consoleOutput.delete(1.0, END)


class Blog2EpubGui(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)                 
        self.master = master
        self.consoleOutput = Text(self.master)
        self.urlEntry = Entry(self.master, width=10)
        self.limitEntry = Entry(self.master, width=10)
        self.skipEntry = Entry(self.master, width=10)
        self.interface = TkInterface(self.consoleOutput, self.master.update)
        self.init_window()

    def _get_params(self):
        return {
            'interface': self.interface,
            'url': self.urlEntry.get(),
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

    def init_window(self):
        self.master.title("Blog2Epub")
        # Url:
        Label(self.master, text="Url:").grid(row=0)
        self.urlEntry.grid(row=0, column=1, columnspan=2, sticky=W+E)
        # Button:
        downloadButton = Button(self.master, text="Download", command=self.download)
        downloadButton.grid(row=0, column=3)
        # Limit:
        Label(self.master, text="Limit:").grid(row=1)
        self.limitEntry.grid(row=1, column=1)
        # Skip:
        Label(self.master, text="Skip:").grid(row=1, column=2)
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

    def download(self):
        self.interface.clear()
        self.interface.print('Downloading...')
        blog2epub = Blog2Epub(self._get_params())
        blog2epub.download()


def main():
    root = Tk()
    root.resizable(False, False)
    Blog2EpubGui(root)
    root.mainloop() 