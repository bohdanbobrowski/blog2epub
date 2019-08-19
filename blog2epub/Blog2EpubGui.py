#!/usr/bin/env python3
# -*- coding : utf-8 -*-
import tkinter as tk
import sys

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface
from urllib import parse

class TkInterface(EmptyInterface):

    def __init__(self, consoleOutput):
        self.consoleOutput = consoleOutput

    def print(self, text):
        self.consoleOutput.insert(tk.INSERT, text)

    def exception(self, e):
        self.consoleOutput.insert(tk.INSERT, e)


class Blog2EpubGui(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)                 
        self.master = master
        self.consoleOutput = tk.Text(self.master)
        self.urlEntry = tk.Entry(self.master, width=10)
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
        limitEntry = tk.Entry(self.master, width=10)
        limitEntry.grid(row=1, column=1)
        # Skip:
        tk.Label(self.master, text="Skip:").grid(row=1, column=2)
        skipEntry = tk.Entry(self.master, width=10)
        skipEntry.grid(row=1, column=3)
        # Text
        self.consoleOutput.grid(row=2, columnspan=4)
        self.consoleOutput.config(state=tk.DISABLED, bg='black', fg='white')

    def download(self):
        params = {
            'interface': TkInterface(self.consoleOutput),
            'url': self.urlEntry.get(),
        }
        self.consoleOutput.insert(tk.INSERT, self.urlEntry.get())
        blog2epub = Blog2Epub(params)
        blog2epub.download()


def main():
    root = tk.Tk()
    # root.geometry("600x600")
    app = Blog2EpubGui(root)
    root.mainloop() 