import logging
import os
import platform
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from urllib import parse

if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

import yaml
from kivy.app import App
from kivy.clock import mainthread
from kivy.config import Config
from kivy.core.window import Window
from kivy.metrics import Metrics, dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from blog2epub.Blog2Epub import BadUrlException, Blog2Epub
from blog2epub.Common import asset_path
from blog2epub.crawlers.Crawler import EmptyInterface

SIZE = 3 / Metrics.density / Metrics.density
F_SIZE = 3 / Metrics.density

Config.set("input", "mouse", "mouse,multitouch_on_demand")

now = datetime.now()
date_time = now.strftime("%Y-%m-%d[%H.%M.%S]")
logging_filename = os.path.join(
    str(Path.home()), ".blog2epub", f"blog2epub_{date_time}.log"
)


logging.basicConfig(
    filename=logging_filename,
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class StyledLabel(Label):
    def __init__(self, **kwargs):
        super(StyledLabel, self).__init__(**kwargs)
        self.font_size = dp(10 * F_SIZE)
        self.font_name = "RobotoMono-Regular"
        self.width = dp(40 * F_SIZE)
        self.size_hint = (None, 1)


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super(StyledTextInput, self).__init__(**kwargs)
        self.font_size = dp(8 * F_SIZE)
        self.font_name = "RobotoMono-Regular"
        self.halign = "center"
        self.valign = "middle"
        self.size_hint = kwargs.get("size_hint", (0.25, 1))
        self.text = kwargs.get("text", "")


class StyledButton(Button):
    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.font_size = dp(10 * F_SIZE)
        self.font_name = "RobotoMono-Regular"
        self.width = dp(80 * F_SIZE)
        self.size_hint = (None, 1)


class Blog2EpubKivyWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(Blog2EpubKivyWindow, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(6 * SIZE)
        self.spacing = dp(2 * SIZE)
        self.settings = Blog2EpubSettings()

        self.row1 = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.1), spacing=dp(2 * SIZE)
        )
        self.add_widget(self.row1)

        self.row1.add_widget(StyledLabel(text="Url:"))
        self.url_entry = StyledTextInput(
            size_hint=(0.8, 1), text=self.settings.get("url")
        )
        self.row1.add_widget(self.url_entry)
        self.download_button = StyledButton(text="Download")
        self.download_button.bind(on_press=self.download)
        self.row1.add_widget(self.download_button)

        self.row2 = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.1), spacing=dp(2 * SIZE)
        )
        self.add_widget(self.row2)

        self.row2.add_widget(StyledLabel(text="Limit:"))
        self.limit_entry = StyledTextInput(text=self.settings.get("limit"))
        self.row2.add_widget(self.limit_entry)

        self.row2.add_widget(StyledLabel(text="Skip:"))
        self.skip_entry = StyledTextInput(text=self.settings.get("skip"))
        self.row2.add_widget(self.skip_entry)

        self.about_button = StyledButton(text="About")
        self.about_button.bind(on_press=self.about_popup)
        self.row2.add_widget(self.about_button)

        self.console = TextInput(
            font_size=dp(6 * F_SIZE),
            font_name="RobotoMono-Regular",
            background_color="black",
            foreground_color="white",
            size_hint=(1, 0.88),
            readonly=True,
        )
        self.add_widget(self.console)
        self.interface = KivyInterface(self.console_output, self.console_clear)

    @mainthread
    def console_output(self, text: str):
        self.console.text = self.console.text + str(text) + "\n"

    @mainthread
    def console_clear(self):
        self.console.text = ""

    def _get_url(self):
        if parse.urlparse(self.url_entry.text):
            return self.url_entry.text
        raise BadUrlException("Blog url is not valid.")

    @staticmethod
    def _is_int(value) -> Optional[int]:
        try:
            int(value)
            return int(value)
        except ValueError:
            return None

    def _get_params(self):
        return {
            "interface": self.interface,
            "url": self._get_url(),
            "include_images": True,
            "images_height": 800,
            "images_width": 600,
            "images_quality": 40,
            "start": None,
            "end": None,
            "limit": self._is_int(self.limit_entry.text),
            "skip": self._is_int(self.skip_entry.text),
            "force_download": False,
            "file_name": None,
            "cache_folder": os.path.join(str(Path.home()), ".blog2epub"),
            "destination_folder": str(Path.home()),
        }

    def _download_ebook(self, blog2epub: Blog2Epub):
        self.interface.print("Downloading...")
        blog2epub.download()
        self.download_button.disabled = False

    def download(self, instance):
        self.interface.clear()
        self.download_button.disabled = True
        self.save_settings()
        download_thread = threading.Thread(
            target=self._download_ebook,
            kwargs={"blog2epub": Blog2Epub(self._get_params())},
        )
        download_thread.start()

        self.download_button.disabled = False

    def save_settings(self):
        self.settings.set("url", self.url_entry.text)
        self.settings.set("limit", self.limit_entry.text)
        self.settings.set("skip", self.skip_entry.text)
        self.settings.save()

    def about_popup(self, instance):
        about_content = BoxLayout(orientation="vertical")
        about_content.add_widget(
            Image(
                source=asset_path("blog2epub.png"),
                allow_stretch=True,
                size_hint=(1, 0.7),
            )
        )
        about_content.add_widget(AboutPopupLabel(text=f"v. {Blog2Epub.version}"))
        about_content.add_widget(AboutPopupLabel(text="by Bohdan Bobrowski"))

        def about_url_click(inst):
            webbrowser.open("https://github.com/bohdanbobrowski/blog2epub")

        about_content.add_widget(
            Button(
                text="github.com/bohdanbobrowski/blog2epub",
                font_size=dp(8 * F_SIZE),
                font_name="RobotoMono-Regular",
                size_hint=(1, 0.1),
                on_press=about_url_click,
            )
        )
        about_popup = Popup(
            title="Blog2Epub",
            title_size=dp(10 * F_SIZE),
            title_font="RobotoMono-Regular",
            content=about_content,
            size_hint=(None, None),
            size=(dp(210 * F_SIZE), dp(180 * F_SIZE)),
        )
        about_popup.open()


class AboutPopupLabel(Label):
    def __init__(self, **kwargs):
        super(AboutPopupLabel, self).__init__(**kwargs)
        self.font_size = dp(8 * F_SIZE)
        self.font_name = "RobotoMono-Regular"
        self.size_hint = (1, 0.1)


class KivyInterface(EmptyInterface):
    def __init__(self, console_output, console_clear):
        self.console_output = console_output
        self.console_clear = console_clear

    def print(self, text: str):
        logging.info(text)
        self.console_output(text)

    @staticmethod
    def notify(title, subtitle, message, cover):
        if platform.system() == "Darwin":
            app_icon = os.path.join(os.path.dirname(sys.executable), "blogspot.png")
            command = [
                "terminal-notifier",
                f"-title {title}",
                f"-subtitle {subtitle}",
                f"-message {message}",
                f"-contentImage {cover}",
                f"-sound chime",
                f"-appIcon {app_icon}",
                f"-open file:{message}",
            ]
            cmd = " ".join(command)
            os.system(f"terminal-notifier {cmd}")
        if platform.system() == "Linux":
            subprocess.Popen(["notify-send", subtitle + ": " + message])

    def exception(self, e):
        logging.error("Exception: " + str(e))
        self.print("Exception: " + str(e))

    def clear(self):
        self.console_clear()


class Blog2EpubSettings:
    def __init__(self):
        self.path = os.path.join(str(Path.home()), ".blog2epub")
        self._prepare_path()
        self.fname = os.path.join(self.path, "blog2epub.yml")
        self._data = self._read()

    def _prepare_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _read(self):
        if not os.path.isfile(self.fname):
            self._data = self._get_default()
            self.save()
        with open(self.fname, "rb") as stream:
            data_in_file = yaml.safe_load(stream)
            data = self._get_default()
            for k, v in data.items():
                if k in data_in_file:
                    data[k] = data_in_file[k]
        return data

    def _get_default(self) -> Dict:
        return {"url": "", "limit": "", "skip": ""}

    def save(self):
        with open(self.fname, "w") as outfile:
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
        self.title = f"blog2epub - v. {Blog2Epub.version}"
        if platform.system() == "Darwin":
            self.icon = asset_path("blog2epub.icns")
        elif platform.system() == "Windows":
            self.icon = asset_path("blog2epub_256px.png")
        else:
            self.icon = asset_path("blog2epub.svg")

    def build(self):
        Window.resizable = False
        Window.size = (dp(300 * SIZE), dp(200 * SIZE))
        return Blog2EpubKivyWindow()


def main():
    Blog2EpubKivy().run()


if __name__ == "__main__":
    main()
