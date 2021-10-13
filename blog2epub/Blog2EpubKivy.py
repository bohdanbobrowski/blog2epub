#!/usr/bin/env python3
# -*- coding : utf-8 -*-
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

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
Config.set('graphics', 'resizable', False)


class StyledLabel(Label):

    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        self.font_size = '25sp'
        self.size_hint = kwargs.get('size_hint', (0.125, 0.10))


class StyledTextInput(TextInput):

    def __init__(self, **kwargs):
        super(StyledTextInput, self).__init__(**kwargs)
        self.font_size = '25sp'
        self.halign = 'center'
        self.valign = 'middle'
        self.size_hint = kwargs.get('size_hint', (0.25, 0.10))
        self.text = kwargs.get('text', '')


class StyledButton(Button):

    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.font_size = '25sp'
        self.size_hint = kwargs.get('size_hint', (0.25, 0.10))


class Blog2EpubKivyWindow(StackLayout):

    def __init__(self, **kwargs):
        super(Blog2EpubKivyWindow, self).__init__(**kwargs)
        self.orientation = 'lr-tb'
        self.padding = 10
        self.spacing = 10
        self.settings = Blog2EpubSettings()

        self.add_widget(StyledLabel(text='Url:'))
        self.url_entry = StyledTextInput(size_hint=(0.625, 0.10), text=self.settings.get('url'))        
        self.add_widget(self.url_entry)
        self.download_button = StyledButton(text='Download')
        self.add_widget(self.download_button)

        self.add_widget(StyledLabel(text='Limit:'))
        self.limit_entry = StyledTextInput(text=self.settings.get('limit'))
        self.add_widget(self.limit_entry)

        self.add_widget(StyledLabel(text='Skip:'))
        self.skip_entry = StyledTextInput(text=self.settings.get('limit'))
        self.add_widget(self.skip_entry)

        self.about_button = StyledButton(text='About')
        self.about_button.bind(on_press = self.about_popup)
        self.add_widget(self.about_button)

        self.console_output = TextInput(font_size='15sp', font_name='RobotoMono-Regular', size_hint=(1, 0.77), readonly=True)
        self.add_widget(self.console_output)

    def about_popup(self, instance):
        about_content = Label(text='Hello world')
        about_popup = Popup(
            title='Test popup',
            content=about_content,
            size_hint=(None, None), size=(400, 400)
        )
        about_popup.open()

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


class Blog2EpubKivy(App):

    def build(self):
        Window.resizable = False
        Window.size = (800,600)
        return Blog2EpubKivyWindow()
