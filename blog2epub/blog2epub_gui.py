import logging
import os
import re
import sys
import webbrowser
import math
import time
from datetime import datetime
from itertools import cycle
from pathlib import Path
from threading import Thread
from typing import Optional, List
from urllib import parse

from kivy.uix.anchorlayout import AnchorLayout  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivymd.uix.datatables import MDDataTable  # type: ignore
from kivymd.uix.tab import MDTabsBase, MDTabs  # type: ignore
from kivymd.uix.textfield import MDTextField  # type: ignore
from kivy.utils import platform  # type: ignore

from plyer import filechooser, notification, email  # type: ignore

from blog2epub.common.book import Book
from blog2epub.models.book import ArticleModel

if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config  # type: ignore

Config.set("input", "mouse", "mouse,multitouch_on_demand")
Config.set("graphics", "resizable", False)

from kivymd.app import MDApp  # type: ignore
from kivy.clock import mainthread  # type: ignore
from kivy.core.window import Window  # type: ignore
from kivy.metrics import Metrics, sp  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDRoundFlatIconButton  # type: ignore
from kivy.uix.image import Image  # type: ignore
from kivymd.uix.label import MDLabel  # type: ignore
from kivy.uix.popup import Popup  # type: ignore
from kivy.uix.textinput import TextInput  # type: ignore
from kivymd.uix.dropdownitem import MDDropDownItem  # type: ignore # noqa

from blog2epub import Blog2Epub
from blog2epub.common.assets import asset_path, open_file
from blog2epub.common.crawler import prepare_url
from blog2epub.common.exceptions import BadUrlException
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.common.settings import Blog2EpubSettings

UI_FONT_NAME = asset_path("MartianMono-Regular.ttf")
SETTINGS = Blog2EpubSettings()
URL_HISTORY_ITERATOR = cycle(SETTINGS.data.history)


def get_previous():
    if len(SETTINGS.data.history) > 2:
        for x in range(0, len(SETTINGS.data.history) - 2):
            next(URL_HISTORY_ITERATOR)
    return next(URL_HISTORY_ITERATOR)


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


class UrlTextInput(MDTextField):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # ↑ up
        if keycode[0] == 273 and (
            self.text == "" or self.text in SETTINGS.data.history
        ):
            self.text = get_previous()
        # ↓ down
        if keycode[0] == 274 and (
            self.text == "" or self.text in SETTINGS.data.history
        ):
            self.text = next(URL_HISTORY_ITERATOR)
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class Tab(MDBoxLayout, MDTabsBase):
    pass


class Blog2EpubKivyWindow(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.articles_data = []
        self.blog2epub = None
        self.download_thread = None
        self.ebook_data = None

        self.tabs = MDTabs()
        self.add_widget(self.tabs)

        self._define_tab_download()
        self.tabs.add_widget(self.tab_download)

        self._define_tab_select()
        self.tabs.add_widget(self.tab_select)

        self._define_tab_generate()
        self.tabs.add_widget(self.tab_generate)

        self._define_tab_about()
        self.tabs.add_widget(self.tab_about)

        self.interface = KivyInterface(self.console_output, self.console_clear)

    def _define_tab_download(self):
        self.tab_download = Tab(
            title="Download",
            icon="download",
            orientation="vertical",
            spacing=sp(10),
            padding=sp(16),
        )

        url_row = self._get_url_row()
        self.tab_download.add_widget(url_row)

        params_row = self._get_params_row()
        self.tab_download.add_widget(params_row)

        self.console = TextInput(
            font_size=sp(16),
            font_name=UI_FONT_NAME,
            background_color="black",
            foreground_color="white",
            size_hint=(1, 0.88),
            readonly=True,
        )
        self.tab_download.add_widget(self.console)

    @mainthread
    def _define_data_tables(self):
        self.articles_table = MDDataTable(
            use_pagination=False,
            check=False,
            column_data=[
                ("", 0),
                ("", sp(10)),
                ("No.", sp(10)),
                ("Title", sp(125)),
            ],
            row_data=[],
            rows_num=1000,
            padding=0,
            elevation=0,
        )
        self.articles_table.bind(on_row_press=self._on_row_press)
        self.tab_select.add_widget(self.articles_table)

    def _on_row_press(self, instance_table, cell_row):
        row_index = math.floor(cell_row.index / 4)
        if self.articles_data[row_index][0]:
            self.articles_data[row_index][0] = False
        else:
            self.articles_data[row_index][0] = True
        self.articles_table.update_row_data(
            self.articles_table, self._get_articles_rows()
        )
        self._update_tab_generate()

    def _define_tab_select(self):
        self.tab_select = Tab(
            title="Select",
            icon="format-list-bulleted-type",
            orientation="vertical",
            spacing=sp(1),
            padding=sp(16),
            disabled=True,
        )
        self._define_data_tables()

    def _define_tab_generate(self):
        self.tab_generate = Tab(
            title="Generate",
            icon="cog",
            orientation="vertical",
            spacing=sp(1),
            padding=sp(16),
        )

        self.selected_label = MDLabel(
            text=f"Selected {0} articles.",
            halign="center",
            font_size=sp(16),
            font_name=UI_FONT_NAME,
            size_hint=(1, 0.2),
        )
        tab_layout = BoxLayout(orientation="vertical", spacing=sp(10), padding=sp(16))
        tab_layout.add_widget(self.selected_label)

        email_row = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.12),
        )
        email_entry = MDTextField(
            hint_text="Email address to send the generated ebook:",
            icon_right="email",
            text=SETTINGS.data.email,
            helper_text="Need to be a correct e-mail address",
            helper_text_mode="on_error",
        )
        email_entry.bind(text=self._validate_email)
        email_row.add_widget(email_entry)
        tab_layout.add_widget(email_row)

        self.destination_button = MDRoundFlatIconButton(
            icon="folder",
            text=f"Destination folder: {SETTINGS.data.destination_folder}",
            font_size=sp(16),
        )
        self.destination_button.bind(on_press=self.select_destination_folder)
        self._put_element_in_anchor_layout(self.destination_button, tab_layout)

        self.generate_button = MDRoundFlatIconButton(
            icon="book-open-page-variant",
            text="Generate",
            font_size=sp(16),
            disabled=True,
        )
        self.generate_button.bind(on_press=self.generate)
        self._put_element_in_anchor_layout(self.generate_button, tab_layout)

        self.tab_generate.add_widget(tab_layout)

    def select_destination_folder(self, instance):
        path = filechooser.choose_dir(
            title="Select ebook destination",
        )
        logging.info(f"Selected path: {path}")
        SETTINGS.data.destination_folder = path[0]
        SETTINGS.save()

        self.destination_button.text = (
            f"Destination folder: {SETTINGS.data.destination_folder}"
        )

    @staticmethod
    def _put_element_in_anchor_layout(element, layout):
        anchor_layout = AnchorLayout(anchor_x="center", size_hint=(1, 0.04))
        anchor_layout.add_widget(element)
        layout.add_widget(anchor_layout)

    def _update_tab_generate(self):
        selected_no = 0
        for art in self.articles_data:
            if art[0]:
                selected_no += 1
        self.selected_label.text = f"Selected {selected_no} articles."

        if selected_no > 0:
            self.generate_button.disabled = False
        else:
            self.generate_button.disabled = True

    def _define_tab_about(self):
        self.tab_about = Tab(
            title="About",
            icon="information-variant",
            orientation="vertical",
            spacing=sp(1),
            padding=sp(16),
        )
        self.tab_about.add_widget(
            Image(
                source=asset_path("blog2epub.png"),
                allow_stretch=True,
                size_hint=(1, 0.7),
            )
        )
        self.tab_about.add_widget(
            MDLabel(
                text=f"v. {Blog2Epub.version}",
                halign="center",
                font_size=sp(16),
                font_name=UI_FONT_NAME,
                size_hint=(1, 0.1),
            )
        )
        self.tab_about.add_widget(
            MDLabel(
                text="by Bohdan Bobrowski",
                halign="center",
                font_size=sp(16),
                font_name=UI_FONT_NAME,
                size_hint=(1, 0.1),
            )
        )

        def about_url_click(inst):
            webbrowser.open("https://github.com/bohdanbobrowski/blog2epub")

        self.tab_about.add_widget(
            MDRoundFlatIconButton(
                text="github.com/bohdanbobrowski/blog2epub",
                font_size=sp(16),
                font_name=UI_FONT_NAME,
                size_hint=(1, 0.1),
                on_press=about_url_click,
                icon="git",
            )
        )

    def _get_url_row(self) -> MDBoxLayout:
        url_row = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.12),
        )

        self.url_entry = UrlTextInput(
            hint_text="Blog url:",
            text=SETTINGS.data.url,
            helper_text="Press up/down to browse in url history",
            icon_right="clipboard-flow",
        )
        url_row.add_widget(self.url_entry)
        return url_row

    def _get_params_row(self) -> MDBoxLayout:
        params_row = MDBoxLayout(
            orientation="horizontal", size_hint=(1, 0.12), spacing=sp(10)
        )

        self.limit_entry = MDTextField(
            text=SETTINGS.data.limit,
            input_type="number",
            hint_text="Articles limit:",
            icon_right="numeric",
        )
        self.limit_entry.bind(text=self._validate_limit)
        params_row.add_widget(self.limit_entry)

        self.skip_entry = MDTextField(
            text=SETTINGS.data.skip,
            input_type="number",
            hint_text="Skip:",
            icon_right="numeric",
        )
        self.skip_entry.bind(text=self._validate_skip)
        params_row.add_widget(self.skip_entry)

        self.download_button = MDRoundFlatIconButton(
            icon="download",
            text="Download",
            size_hint=(0.2, 1),
        )
        self.download_button.bind(on_press=self.download)
        params_row.add_widget(self.download_button)
        return params_row

    def _validate_limit(self, input_widget, text):
        input_widget.text = " ".join(re.findall(r"\d+", text))
        SETTINGS.data.limit = input_widget.text

    def _validate_skip(self, input_widget, text):
        input_widget.text = " ".join(re.findall(r"\d+", text))
        SETTINGS.data.skip = input_widget.text

    def _validate_email(self, input_widget, text):
        if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", text) or text == "":
            input_widget.error = False
            SETTINGS.data.email = text
        else:
            input_widget.error = True

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
        if platform == "android":
            cache_folder = self.user_data_dir
        else:
            cache_folder = os.path.join(str(Path.home()), ".blog2epub")
        destination_folder = str(Path.home())
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
            "cache_folder": cache_folder,
            "destination_folder": destination_folder,
        }

    def _download_ebook(self, blog2epub: Blog2Epub):
        blog2epub.download()
        self._enable_download_button()
        if len(blog2epub.crawler.articles) > 0:
            self.tab_select.disabled = False
            self._update_articles_data(blog2epub.crawler.articles)
            self.articles_table.update_row_data(
                self.articles_table, self._get_articles_rows()
            )
            SETTINGS.data.language = blog2epub.crawler.language
            self.ebook_data = blog2epub.crawler.get_book_data()
            self.articles_table.update_row_data(
                self.articles_table, self._get_articles_rows()
            )
            self._update_tab_generate()
        if not blog2epub.crawler.cancelled:
            self.interface.print("Download completed.")
            notification.notify(
                title="blog2epub - download completed",
                message=f"{blog2epub.crawler.url}",
                timeout=2,
            )
            self._switch_tab("Select")

    @mainthread
    def _switch_tab(self, tab_title: str):
        self.tabs.switch_tab(name_tab=tab_title, search_by="title")

    def _get_articles_to_save(self) -> List[ArticleModel]:
        articles_to_save = []
        for x in range(0, len(self.articles_data)):
            if self.articles_data[x][0]:
                articles_to_save.append(self.ebook_data.articles[x])
        return articles_to_save

    def generate(self, instance):
        if self.ebook_data:
            ebook = Book(
                book_data=self.ebook_data,
                configuration=SETTINGS.data,
                interface=self.interface,
                destination_folder=SETTINGS.data.destination_folder,
            )
            ebook.save(self._get_articles_to_save())
            self.popup_success(ebook)

    def _update_articles_data(self, articles: List):
        no = 1
        self.articles_data = []
        for article in articles:
            self.articles_data.append([True, no, article.title])
            no += 1

    def _get_articles_rows(self):
        temp_data = []
        for row in self.articles_data:
            if row[0]:
                icon = "checkbox-outline"
            else:
                icon = "checkbox-blank-outline"
            temp_data.append(
                (
                    "",
                    (icon, [0, 0, 0, 1], ""),
                    row[1],
                    row[2],
                )
            )
        return temp_data

    def download(self, instance):
        self.interface.clear()
        self._disable_download_button()
        self.articles_table.update_row_data(self.articles_table, [])
        self.tab_select.disabled = True
        self.save_settings()
        self.blog2epub = Blog2Epub(self._get_params())
        self.download_thread = Thread(
            target=self._download_ebook,
            kwargs={"blog2epub": self.blog2epub},
        )
        self.download_thread.start()

    def cancel_download(self, instance):
        if self.blog2epub:
            self.blog2epub.crawler.cancelled = True
            while self.blog2epub.crawler.active:
                logging.info("Cancelling download...")
                time.sleep(1)
            self.interface.print("Download cancelled.")
            self._update_articles_data([])
            self.articles_table.update_row_data([], [])
            self.ebook_data = self.blog2epub = None
            self._update_tab_generate()

    def _disable_download_button(self):
        self.interface.print("Downloading...")
        # self.download_button.disabled = True
        self.download_button.icon = "cancel"
        self.download_button.text = "Cancel"
        self.download_button.unbind(on_press=self.download)
        self.download_button.bind(on_press=self.cancel_download)

    def _enable_download_button(self):
        self.download_button.disabled = False
        self.download_button.icon = "download"
        self.download_button.text = "Download"
        self.download_button.unbind(on_press=self.cancel_download)
        self.download_button.bind(on_press=self.download)

    def save_settings(self):
        """TODO: This should be removed from here"""
        SETTINGS.data.url = prepare_url(self.url_entry.text)
        SETTINGS.data.limit = self.limit_entry.text
        SETTINGS.data.skip = self.skip_entry.text
        SETTINGS.save()

    @mainthread
    def popup_success(self, ebook: Book):
        self.success(ebook)

    def success(self, ebook: Book):
        success_content = MDBoxLayout(orientation="vertical")
        epub_cover_image_widget = MDBoxLayout(
            padding=sp(20),
            size_hint=(1, 1),
        )
        epub_cover_image_widget.add_widget(
            Image(
                source=asset_path(str(ebook.cover_image_path)),
                allow_stretch=True,
                size_hint=(1, 1),
            )
        )
        success_content.add_widget(epub_cover_image_widget)

        def open_ebook_in_default_viewer(inst):
            open_file(ebook.generated_ebook_path)

        def send_ebook_via_email(inst):
            email.send(
                recipient=SETTINGS.data.email,
                subject=f"blog2epub - {ebook.title}",
                text="Now please attach generated file manually :-)",
            )

        buttons_row = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.1),
            spacing=sp(10),
            # padding=sp(16),
        )

        buttons_row.add_widget(
            MDRoundFlatIconButton(
                text="Read epub",
                icon="book-open-variant",
                font_size=sp(16),
                font_name=UI_FONT_NAME,
                size_hint=(0.5, 1),
                on_press=open_ebook_in_default_viewer,
            )
        )
        if SETTINGS.data.email:
            buttons_row.add_widget(
                MDRoundFlatIconButton(
                    text="Send epub via e-mail",
                    icon="email",
                    font_size=sp(16),
                    font_name=UI_FONT_NAME,
                    size_hint=(0.5, 1),
                    on_press=send_ebook_via_email,
                )
            )
        success_content.add_widget(buttons_row)

        success_popup = Popup(
            title="Ebook generated successfully:",
            title_size=sp(20),
            title_font=UI_FONT_NAME,
            content=success_content,
            size_hint=(None, None),
            size=(sp(700), sp(500)),
        )
        success_popup.open()


class KivyInterface(EmptyInterface):
    def __init__(self, console_output, console_clear):
        self.console_output = console_output
        self.console_clear = console_clear

    def print(self, text: str):
        logging.info(text)
        self.console_output(text)

    def exception(self, e):
        logging.error("Exception: " + str(e))
        self.print("Exception: " + str(e))

    def clear(self):
        self.console_clear()


class Blog2EpubKivy(MDApp):
    def __init__(self):
        super().__init__()
        self.title = f"blog2epub - v. {Blog2Epub.version}"
        logging.info(self.title)
        logging.debug(f"Metrics.density = {Metrics.density}")
        if platform == "linux":
            self.icon = asset_path("blog2epub.svg")
        elif platform == "win":
            self.icon = asset_path("blog2epub_256px.png")
        else:
            self.icon = asset_path("blog2epub.icns")

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        Window.resizable = False
        Window.size = (sp(640), sp(480))
        return Blog2EpubKivyWindow()


def main():
    Blog2EpubKivy().run()


if __name__ == "__main__":
    main()
