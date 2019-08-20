#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import tkinter as tk
import sys
import os
from pathlib import Path

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface
from urllib import parse

class TkInterface(EmptyInterface):

    def __init__(self, consoleOutput, refresh):
        self.consoleOutput = consoleOutput
        self.refresh = refresh

    def print(self, text):
        self.consoleOutput.insert(tk.END, text + '\n')
        self.consoleOutput.see('end')
        self.refresh()

    def exception(self, e):
        self.consoleOutput.insert(tk.END, e + '\n')
        self.consoleOutput.see('end')
        self.refresh()


class Blog2EpubGui(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)                 
        self.master = master
        self.consoleOutput = tk.Text(self.master)
        self.urlEntry = tk.Entry(self.master, width=10)
        self.limitEntry = tk.Entry(self.master, width=10)
        self.skipEntry = tk.Entry(self.master, width=10)
        self.init_window()

    def init_window(self):
        self.master.title("Blog2Epub")
        # Url:
        tk.Label(self.master, text="Url:").grid(row=0)
        self.urlEntry.grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E)
        # Button:
        downloadButton = tk.Button(self.master, text="Download", command=self.download)
        downloadButton.grid(row=0, column=3)
        # Limit:
        tk.Label(self.master, text="Limit:").grid(row=1)
        self.limitEntry.grid(row=1, column=1)
        # Skip:
        tk.Label(self.master, text="Skip:").grid(row=1, column=2)
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
        self.consoleOutput.delete(1.0,tk.END)
        interface = TkInterface(self.consoleOutput, self.update_idletasks)
        interface.print('Downloading...')
        params = {
            'interface': interface,
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
        blog2epub = Blog2Epub(params)
        blog2epub.download()


def main():
    root = tk.Tk()
    root.resizable(False, False)
    # root.geometry("600x600")
    app = Blog2EpubGui(root)
    root.mainloop() 