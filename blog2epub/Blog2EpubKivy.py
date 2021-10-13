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
import threading
import webbrowser

from blog2epub.Blog2Epub import Blog2Epub
from blog2epub.crawlers.Crawler import EmptyInterface

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

now = datetime.now()
date_time = now.strftime("%Y-%m-%d[%H.%M.%S]")
logging_filename = os.path.join(str(Path.home()), '.blog2epub', 'blog2epub_{}.log'.format(date_time))


logging.basicConfig(
    filename=logging_filename,
    encoding='utf-8',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_image_file(filename):    
    in_binaries = os.path.join(os.path.dirname(sys.executable), filename)
    in_sources = os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'images', filename)
    if os.path.isfile(in_binaries):
        return in_binaries
    if os.path.isfile(in_sources):
        return in_sources        
    return False


class StyledLabel(Label):

    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        self.font_size = '25dp'
        self.width = 100
        self.size_hint = (None, 1)


class StyledTextInput(TextInput):

    def __init__(self, **kwargs):
        super(StyledTextInput, self).__init__(**kwargs)
        self.font_size = '25dp'
        self.font_name = 'RobotoMono-Regular'
        self.halign = 'center'
        self.valign = 'middle'
        self.size_hint = kwargs.get('size_hint', (0.25, 1))
        self.text = kwargs.get('text', '')


class StyledButton(Button):

    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.font_size = '25dp'
        self.width = 150
        self.size_hint = (None, 1)


class Blog2EpubKivyWindow(BoxLayout):

    def __init__(self, **kwargs):
        super(Blog2EpubKivyWindow, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.settings = Blog2EpubSettings()

        self.row1 = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing = 10
        )
        self.add_widget(self.row1)

        self.row1.add_widget(StyledLabel(text='Url:'))
        self.url_entry = StyledTextInput(size_hint=(0.5, 1), text=self.settings.get('url'))        
        self.row1.add_widget(self.url_entry)
        self.download_button = StyledButton(text='Download')
        self.download_button.bind(on_press = self.download)
        self.row1.add_widget(self.download_button)

        self.row2 = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing = 10
        )
        self.add_widget(self.row2)

        self.row2.add_widget(StyledLabel(text='Limit:'))
        self.limit_entry = StyledTextInput(text=self.settings.get('limit'))
        self.row2.add_widget(self.limit_entry)

        self.row2.add_widget(StyledLabel(text='Skip:'))
        self.skip_entry = StyledTextInput(text=self.settings.get('skip'))
        self.row2.add_widget(self.skip_entry)

        self.about_button = StyledButton(text='About')
        self.about_button.bind(on_press = self.about_popup)
        self.row2.add_widget(self.about_button)

        self.console_output = TextInput(
            font_size='15dp',
            font_name='RobotoMono-Regular',
            background_color='black',
            foreground_color='white',
            size_hint=(1, 0.88),            
            readonly=True,
            padding_x=['10dp', '10dp']
        )
        self.add_widget(self.console_output)
        self.interface = KivyInterface(self.console_output)

    def _get_url(self):
        if parse.urlparse(self.url_entry.text):
            return self.url_entry.text            
        raise Exception('Blog url is not valid.')        

    @staticmethod
    def _is_int(value):
        try:
            int(value)
            return int(value)
        except:
            return None          

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
            'limit': self._is_int(self.limit_entry.text),
            'skip': self._is_int(self.skip_entry.text),
            'force_download': False,
            'file_name': None,
            'cache_folder': os.path.join(str(Path.home()), '.blog2epub'),
            'destination_folder': str(Path.home()),
        }

    def _download_ebook(self, blog2epub):
        self.interface.print('Downloading...')
        blog2epub.download()
        self.download_button.disabled = False

    def download(self, instance):
        self.interface.clear()
        self.download_button.disabled = True
        try:
            self.saveSettings()            
            download_thread = threading.Thread(target=self._download_ebook, kwargs={'blog2epub':Blog2Epub(self._get_params())})
            download_thread.start()                        
        except Exception as e:
            self.download_button.disabled = False
            self.interface.exception(e)
   
    def saveSettings(self):
        self.settings.set('url', self.url_entry.text)
        self.settings.set('limit', self.limit_entry.text)
        self.settings.set('skip', self.skip_entry.text)
        self.settings.save()

    def about_popup(self, instance):
        about_content = BoxLayout(orientation='vertical')
        about_content.add_widget(Image(
            source = get_image_file('blog2epub.png'),
            allow_stretch = True,
            size_hint=(1, 0.7)
        ))
        about_content.add_widget(AboutPopupLabel(
            text = 'v. {}'.format(Blog2Epub.VERSION)            
        ))        
        about_content.add_widget(AboutPopupLabel(
            text = 'by Bohdan Bobrowski'
        ))   

        def about_url_click(instance):
            webbrowser.open("https://github.com/bohdanbobrowski/blogspot2epub")

        about_content.add_widget(Button(
            text = 'github.com/bohdanbobrowski/blogspot2epub',
            font_size = '20dp',
            size_hint = (1, 0.1),
            on_press = about_url_click
        ))
        about_popup = Popup(
            title = 'Blog2Epub',
            title_size = '30dp',
            content = about_content,
            size_hint = (None, None), size=('500dp', '500dp'),            
        )
        about_popup.open()


class AboutPopupLabel(Label):

    def __init__(self, **kwargs):
        super(AboutPopupLabel, self).__init__(**kwargs)
        self.font_size = '20dp'
        self.size_hint = (1, 0.1)


class KivyInterface(EmptyInterface):
    def __init__(self, console):
        self.console = console

    def print(self, text):
        logging.info(text)
        self.console.text = self.console.text + text + "\n"
 
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
        self.console.text = ""


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

    def __init__(self, **kwargs):
        super(Blog2EpubKivy, self).__init__(**kwargs)
        self.icon = get_image_file('blog2epub.icns')

    def build(self):
        Window.resizable = False
        Window.size = (800,600)
        return Blog2EpubKivyWindow()


def main():
    Blog2EpubKivy().run()
