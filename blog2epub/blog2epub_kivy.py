import logging
import os
import platform
import re
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Optional
from urllib import parse
from itertools import cycle

from blog2epub.common.settings import Blog2EpubSettings

if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config

Config.set("input", "mouse", "mouse,multitouch_on_demand")
Config.set("graphics", "resizable", False)

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.metrics import Metrics, dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from blog2epub import Blog2Epub
from blog2epub.common.assets import asset_path, open_file
from blog2epub.common.crawler import prepare_url
from blog2epub.common.exceptions import BadUrlException
from blog2epub.common.interfaces import EmptyInterface

SIZE = 3 / Metrics.density / Metrics.density
F_SIZE = 3 / Metrics.density
UI_FONT_NAME = asset_path("MartianMono-Regular.ttf")
SETTINGS = Blog2EpubSettings()
URL_HISTORY = SETTINGS.get("history")
URL_HISTORY_ITERATOR = cycle(URL_HISTORY)


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
        self.font_size = dp(6 * F_SIZE)
        self.font_name = UI_FONT_NAME
        self.width = dp(40 * F_SIZE)
        self.size_hint = (None, 1)


class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super(StyledTextInput, self).__init__(**kwargs)
        self.font_size = dp(6 * F_SIZE)
        self.font_name = UI_FONT_NAME
        self.halign = "left"
        self.valign = "middle"
        self.write_tab = False
        self.multiline = False
        self.padding_y = [15, 15]
        self.padding_x = [15, 15]
        self.size_hint = kwargs.get("size_hint", (0.25, 1))
        self.text = kwargs.get("text", "")


class UrlTextInput(StyledTextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 274 and (self.text == "" or self.text in URL_HISTORY):
            self.text = next(URL_HISTORY_ITERATOR)
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class StyledButton(Button):
    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.font_size = dp(6 * F_SIZE)
        self.font_name = UI_FONT_NAME
        self.width = dp(80 * F_SIZE)
        self.size_hint = (None, 1)


class Blog2EpubKivyWindow(BoxLayout):
    def __init__(self, **kwargs):
        super(Blog2EpubKivyWindow, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(6 * SIZE)
        self.spacing = dp(2 * SIZE)

        self.row1 = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.1), spacing=dp(2 * SIZE)
        )
        self.add_widget(self.row1)

        self.row1.add_widget(StyledLabel(text="Url:"))

        hint_text = ""
        if SETTINGS.get("history"):
            hint_text = "Press down to browse in url history"

        self.url_entry = UrlTextInput(
            size_hint=(0.8, 1),
            text=SETTINGS.get("url"),
            hint_text=hint_text,
            input_type="url",
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
        self.limit_entry = StyledTextInput(
            text=SETTINGS.get("limit"), input_type="number"
        )
        self.limit_entry.bind(text=self._allow_only_numbers)
        self.row2.add_widget(self.limit_entry)

        self.row2.add_widget(StyledLabel(text="Skip:"))
        self.skip_entry = StyledTextInput(
            text=SETTINGS.get("skip"), input_type="number"
        )
        self.skip_entry.bind(text=self._allow_only_numbers)
        self.row2.add_widget(self.skip_entry)

        self.about_button = StyledButton(text="About")
        self.about_button.bind(on_press=self.about)
        self.row2.add_widget(self.about_button)

        self.console = TextInput(
            font_size=dp(6 * F_SIZE),
            font_name=UI_FONT_NAME,
            background_color="black",
            foreground_color="white",
            size_hint=(1, 0.88),
            readonly=True,
        )
        self.add_widget(self.console)
        self.interface = KivyInterface(self.console_output, self.console_clear)

    def _suggest_history(self, *kwargs):
        print(kwargs)

    def _allow_only_numbers(self, input_widget, text):
        input_widget.text = " ".join(re.findall(r"\d+", text))

    @mainthread
    def console_output(self, text: str):
        self.console.text = self.console.text + str(text) + "\n"

    @mainthread
    def console_clear(self):
        self.console.text = ""

    def _get_url(self):
        if parse.urlparse(self.url_entry.text):
            self.url_entry.text = prepare_url(self.url_entry.text)
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
            "images_size": (600, 800),
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
        cover_image_path, generated_ebook_path = blog2epub.download()
        self._enable_download_button()
        self.popup_success(cover_image_path, generated_ebook_path)

    def download(self, instance):
        self.interface.clear()
        self._disable_download_button()
        self.save_settings()
        download_thread = Thread(
            target=self._download_ebook,
            kwargs={"blog2epub": Blog2Epub(self._get_params())},
        )
        download_thread.start()

    def _disable_download_button(self):
        self.interface.print("Downloading...")
        self.download_button.disabled = True
        self.download_button.text = "Downloading..."

    def _enable_download_button(self):
        self.download_button.disabled = False
        self.download_button.text = "Download"

    def save_settings(self):
        SETTINGS.set("url", prepare_url(self.url_entry.text))
        SETTINGS.set("limit", self.limit_entry.text)
        SETTINGS.set("skip", self.skip_entry.text)
        SETTINGS.save()

    def about(self, instance):
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
                font_size=dp(6 * F_SIZE),
                font_name=UI_FONT_NAME,
                size_hint=(1, 0.1),
                on_press=about_url_click,
            )
        )
        about_popup = Popup(
            title="Blog2Epub",
            title_size=dp(10 * F_SIZE),
            title_font=UI_FONT_NAME,
            content=about_content,
            size_hint=(None, None),
            size=(dp(210 * F_SIZE), dp(180 * F_SIZE)),
        )
        about_popup.open()

    @mainthread
    def popup_success(self, cover_image_path: str, generated_ebook_path: str):
        self.success(cover_image_path, generated_ebook_path)

    def success(self, cover_image_path: str, generated_ebook_path: str):
        success_content = BoxLayout(orientation="vertical")
        success_content.add_widget(
            Image(
                source=asset_path(cover_image_path),
                allow_stretch=True,
                size_hint=(1, 0.7),
            )
        )

        def success_url_click(inst):
            open_file(generated_ebook_path)

        success_content.add_widget(
            Button(
                text="Click here to open epub",
                font_size=dp(6 * F_SIZE),
                font_name=UI_FONT_NAME,
                size_hint=(1, 0.1),
                on_press=success_url_click,
            )
        )
        success_popup = Popup(
            title="Ebook generated successfully:",
            title_size=dp(10 * F_SIZE),
            title_font=UI_FONT_NAME,
            content=success_content,
            size_hint=(None, None),
            size=(dp(210 * F_SIZE), dp(180 * F_SIZE)),
        )
        success_popup.open()


class AboutPopupLabel(Label):
    def __init__(self, **kwargs):
        Label.__init__(self, **kwargs)
        self.font_size = dp(6 * F_SIZE)
        self.font_name = UI_FONT_NAME
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


class Blog2EpubKivy(App):
    def __init__(self, **kwargs):
        App.__init__(self, **kwargs)
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
