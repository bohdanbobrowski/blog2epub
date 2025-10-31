import logging
import math
import os
import re
import subprocess
import sys
import time
import urllib
import webbrowser
from datetime import datetime
from functools import partial
from itertools import cycle
from threading import Thread

from kivy.uix.anchorlayout import AnchorLayout  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.filechooser import FileChooserListView  # type: ignore
from kivymd.uix.datatables import MDDataTable  # type: ignore
from kivymd.uix.menu import MDDropdownMenu  # type: ignore
from kivymd.uix.tab import MDTabs, MDTabsBase  # type: ignore
from kivymd.uix.textfield import MDTextField  # type: ignore
from plyer import notification  # type: ignore

from blog2epub.common.book import Book
from blog2epub.models.book import ArticleModel
from blog2epub.models.configuration import IMAGE_COL_MODES, IMAGE_SIZES, INCLUDE_IMAGES

if sys.__stdout__ is None or sys.__stderr__ is None:
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config  # type: ignore

# Config.set("input", "mouse", "mouse,multitouch_on_demand")
Config.set("graphics", "resizable", False)

from kivy.clock import mainthread  # type: ignore
from kivy.core.window import Window  # type: ignore
from kivy.metrics import Metrics, sp  # type: ignore
from kivy.uix.image import Image  # type: ignore
from kivy.uix.popup import Popup  # type: ignore
from kivy.uix.textinput import TextInput  # type: ignore
from kivy.utils import platform  # type: ignore
from kivymd.app import MDApp  # type: ignore
from kivymd.uix.boxlayout import MDBoxLayout  # type: ignore
from kivymd.uix.button import MDRoundFlatIconButton  # type: ignore
from kivymd.uix.dropdownitem import MDDropDownItem  # type: ignore # noqa
from kivymd.uix.label import MDLabel  # type: ignore

from blog2epub import Blog2Epub
from blog2epub.common.assets import asset_path
from blog2epub.common.crawler import prepare_port_and_url
from blog2epub.common.exceptions import BadUrlException
from blog2epub.common.interfaces import EmptyInterface
from blog2epub.common.settings import Blog2EpubSettings

USER_DATA_DIR = "."  # TODO: Make it more elegant. This is just workaround.
UI_FONT_NAME = asset_path("LiberationMono-Regular.ttf")

now = datetime.now()
date_time = now.strftime("%Y-%m-%d[%H.%M.%S]")

if __name__ in ["__android__", "__main__"]:
    if platform == "android":
        from android.permissions import Permission, request_permissions  # type: ignore

        request_permissions(
            [
                Permission.INTERNET,
                Permission.WRITE_EXTERNAL_STORAGE,
            ]
        )


class UrlTextInput(MDTextField):
    def __init__(self, *args, **kwargs):
        self.url_history: list[str] = kwargs.pop("url_history", [])  # type: ignore
        self._url_history_iterator = cycle(self.url_history)
        super().__init__(*args, **kwargs)

    def _get_previous_url_history(self):
        if len(self.url_history) > 2:
            for _x in range(0, len(self.url_history) - 2):
                next(self._url_history_iterator)
        return next(self._url_history_iterator)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # ↑ up
        if keycode[0] == 273 and (self.text == "" or self.text in self.url_history):
            self.text = self._get_previous_url_history()
        # ↓ down
        if keycode[0] == 274 and (self.text == "" or self.text in self.url_history):
            self.text = next(self._url_history_iterator)
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class Tab(MDBoxLayout, MDTabsBase):
    pass


class Blog2EpubKivyWindow(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global USER_DATA_DIR
        self.orientation = "vertical"

        self.articles_data = []
        self.blog2epub_settings = Blog2EpubSettings(path=USER_DATA_DIR)
        if platform == "android":
            from android.storage import primary_external_storage_path  # type: ignore

            self.blog2epub_settings.data.destination_folder = os.path.join(primary_external_storage_path(), "Download")

        self.blog2epub = None
        self.download_thread = None
        self.ebook_data = None
        self._generate_lock = False

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

        self.interface = KivyInterface(self.console_output, self.console_clear, self.console_delete_last_line)

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

        self.download_button = MDRoundFlatIconButton(
            icon="download",
            text="Download",
            size_hint=(0.2, 1),
            on_press=self.download,
        )
        self.cancel_button = MDRoundFlatIconButton(
            icon="cancel",
            text="Cancel",
            size_hint=(0.2, 1),
            on_press=self.cancel_download,
        )
        options_row, options_row_2 = self._get_options_rows(platform)
        self.tab_download.add_widget(options_row)
        params_row = self._get_params_row()
        self.tab_download.add_widget(params_row)
        if platform != "android":
            params_row.add_widget(self.download_button)
            self.download_button_container = params_row
        else:
            self.tab_download.add_widget(options_row_2)
            self.download_button_container = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=sp(10))
            self.tab_download.add_widget(self.download_button_container)
            self.download_button_container.add_widget(self.download_button)
        self.console = TextInput(
            font_size=sp(12),
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
        self.articles_table.update_row_data(self.articles_table, self._get_articles_rows())
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

        if platform != "android":
            self.file_chooser = FileChooserListView(dirselect=True)
            self.file_chooser_popup = Popup(
                title="Destination folder",
            )
            self.file_chooser_popup_button = MDRoundFlatIconButton(
                icon="folder",
                text="Select folder",
                font_size=sp(16),
            )
            content_pop_download = MDBoxLayout(
                orientation="vertical",
                size_hint=(1, 1),
                spacing=sp(10),
            )
            content_pop_download.add_widget(self.file_chooser)
            content_pop_download.add_widget(self.file_chooser_popup_button)
            self.file_chooser_popup.add_widget(content_pop_download)

            self.file_chooser_popup_button.bind(on_release=self.get_destination_folder)

            self.destination_button = MDRoundFlatIconButton(
                icon="folder",
                text=f"Destination folder: {self.blog2epub_settings.data.destination_folder}",
                font_size=sp(16),
            )
            self.destination_button.bind(on_press=self.file_chooser_popup.open)
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

    def get_destination_folder(self, *args, **kwargs):
        path = self.file_chooser.path
        logging.info(f"Selected path: {path}")
        if path:
            self.blog2epub_settings.data.destination_folder = path
            self.blog2epub_settings.save()
        self.destination_button.text = f"Destination folder: {self.blog2epub_settings.data.destination_folder}"
        self.file_chooser_popup.dismiss()

    @staticmethod
    def _put_element_in_anchor_layout(element, layout):
        anchor_layout = AnchorLayout(anchor_x="center", size_hint=(1, 0.1))
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

    @staticmethod
    def _open_github_page(inst):
        webbrowser.open("https://github.com/bohdanbobrowski/blog2epub")

    def _define_tab_about(self):
        self.tab_about = Tab(
            title="About",
            icon="information-variant",
            orientation="vertical",
            spacing=sp(1),
            padding=sp(16),
        )
        logo_image = Image(
            source=asset_path("blog2epub.png"),
            allow_stretch=True,
            size_hint=(1, 0.7),
        )
        self.tab_about.add_widget(logo_image)
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

        self.tab_about.add_widget(
            MDRoundFlatIconButton(
                text="blog2epub on github",
                font_size=sp(16),
                font_name=UI_FONT_NAME,
                size_hint=(1, 0.1),
                on_press=self._open_github_page,
                icon="git",
            )
        )

    def _get_url_row(self) -> MDBoxLayout:
        url_row = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.12),
        )
        self.url_entry = UrlTextInput(
            hint_text="Url:",
            text=self.blog2epub_settings.data.url,
            helper_text="" if platform == "android" else "Press up/down to browse in url history",
            url_history=self.blog2epub_settings.data.history,
            icon_right="link-variant",
        )
        url_row.add_widget(self.url_entry)
        return url_row

    def _get_sizes_list(self) -> list[dict]:
        return [
            {
                "text": f"{size[0]}*{size[1]}",
                "on_release": lambda s=size: self._select_images_sizes(s),
            }
            for size in IMAGE_SIZES
        ]

    def _get_color_modes_list(self) -> list[dict]:
        return [
            {
                "text": mode[0],
                "on_release": lambda m=mode: self._select_color_mode(m),
            }
            for mode in IMAGE_COL_MODES.items()
        ]

    @staticmethod
    def _get_color_modes_text(current_mode: bool) -> str:
        for label, value in IMAGE_COL_MODES.items():
            if current_mode == value:
                return label
        return ""

    def _get_include_images_menu(self) -> list[dict]:
        return [
            {
                "text": mode[0],
                "on_release": lambda m=mode: self._select_include_images(m),
            }
            for mode in INCLUDE_IMAGES.items()
        ]

    @staticmethod
    def _get_include_images_text(include: bool) -> str:
        for label, value in INCLUDE_IMAGES.items():
            if include == value:
                return label
        return ""

    def _get_options_rows(self, platform: str) -> tuple[MDBoxLayout, MDBoxLayout]:
        options_row = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=sp(10))
        options_row_2 = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=sp(10))

        # Include Images
        self.include_images_textfield = MDTextField(
            text=self._get_include_images_text(self.blog2epub_settings.data.include_images),
            hint_text="Include images:",
            icon_right="image-size-select-actual",
            readonly=True,
            on_touch_down=self._open_include_images,
        )
        self.include_images_menu = MDDropdownMenu(
            caller=self.include_images_textfield,
            items=self._get_include_images_menu(),
        )
        options_row.add_widget(self.include_images_textfield)

        # Image Sizes
        self.images_sizes_textfield = MDTextField(
            text="*".join([str(x) for x in self.blog2epub_settings.data.images_size]),
            input_type="number",
            hint_text="Images and cover size:",
            icon_right="image-size-select-large",
            readonly=True,
            on_touch_down=self._open_images_sizes,
        )
        self.images_sizes = MDDropdownMenu(
            caller=self.images_sizes_textfield,
            items=self._get_sizes_list(),
        )
        options_row.add_widget(self.images_sizes_textfield)

        self.images_quality = MDTextField(
            text=str(self.blog2epub_settings.data.images_quality),
            input_type="number",
            hint_text="Image quality:",
            icon_right="quality-high",
        )
        self.images_quality.bind(text=self._validate_images_quality)
        if platform == "android":
            options_row_2.add_widget(self.images_quality)
        else:
            options_row.add_widget(self.images_quality)

        # Images Color Mode
        self.images_color_mode_textfield = MDTextField(
            text=self._get_color_modes_text(self.blog2epub_settings.data.images_bw),
            hint_text="Color mode:",
            icon_right="palette",
            readonly=True,
            on_touch_up=self._open_color_modes,
        )
        self.images_color_modes = MDDropdownMenu(
            caller=self.images_color_mode_textfield,
            items=self._get_color_modes_list(),
        )
        if platform == "android":
            options_row_2.add_widget(self.images_color_mode_textfield)
        else:
            options_row.add_widget(self.images_color_mode_textfield)
        return options_row, options_row_2

    def _select_include_images(self, include_images: tuple[str, bool]):
        self.blog2epub_settings.data.include_images = include_images[1]
        self.include_images_textfield.text = include_images[0]

    @staticmethod
    def _checked_if_clicked(
        event_pos: tuple[float, float], caller_pos: tuple[float, float], caller_size: tuple[float, float]
    ) -> bool:
        if event_pos[0] >= caller_pos[0] and event_pos[1] >= caller_pos[1]:
            if event_pos[0] <= caller_pos[0] + caller_size[0] and event_pos[1] <= caller_pos[1] + caller_size[1]:
                return True
        return False

    def _open_include_images(self, caller, event):
        if self._checked_if_clicked(event.pos, caller.pos, caller.size):
            if self.include_images_menu.parent is None:
                self.include_images_menu.open()

    def _select_images_sizes(self, size: tuple[int, int]):
        self.blog2epub_settings.data.images_size = size
        self.images_sizes_textfield.text = "*".join([str(size[0]), str(size[1])])

    def _open_images_sizes(self, caller, event):
        if self._checked_if_clicked(event.pos, caller.pos, caller.size):
            if self.images_sizes.parent is None:
                self.images_sizes.open()

    def _select_color_mode(self, color_mode: tuple[str, bool]):
        self.blog2epub_settings.data.images_bw = color_mode[1]
        self.images_color_mode_textfield.text = color_mode[0]

    def _open_color_modes(self, caller, event):
        if self._checked_if_clicked(event.pos, caller.pos, caller.size):
            if self.images_color_modes.parent is None:
                self.images_color_modes.open()

    def _get_params_row(self) -> MDBoxLayout:
        params_row = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.12), spacing=sp(10))
        self.limit_entry = MDTextField(
            text=self.blog2epub_settings.data.limit,
            input_type="number",
            hint_text="Limit:",
            icon_right="numeric",
        )
        self.limit_entry.bind(text=self._validate_limit)
        params_row.add_widget(self.limit_entry)
        self.skip_entry = MDTextField(
            text=self.blog2epub_settings.data.skip,
            input_type="number",
            hint_text="Skip:",
            icon_right="numeric",
        )
        self.skip_entry.bind(text=self._validate_skip)
        params_row.add_widget(self.skip_entry)
        return params_row

    def _validate_images_quality(self, input_widget, text):
        try:
            text_value = int(" ".join(re.findall(r"\d+", text)))
            if text_value < 1 or text_value > 100:
                text_value = self.blog2epub_settings.data.images_quality
        except ValueError:
            text_value = self.blog2epub_settings.data.images_quality
        input_widget.text = str(text_value)
        self.blog2epub_settings.data.images_quality = text_value

    def _validate_limit(self, input_widget, text):
        input_widget.text = " ".join(re.findall(r"\d+", text))
        self.blog2epub_settings.data.limit = input_widget.text

    def _validate_skip(self, input_widget, text):
        input_widget.text = " ".join(re.findall(r"\d+", text))
        self.blog2epub_settings.data.skip = input_widget.text

    def _validate_email(self, input_widget, text):
        if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", text) or text == "":
            input_widget.error = False
            self.blog2epub_settings.data.email = text
        else:
            input_widget.error = True

    @mainthread
    def console_output(self, text: str, end: str = "\n"):
        self.console.text = self.console.text + str(text) + end

    @mainthread
    def console_clear(self):
        self.console.text = ""

    @mainthread
    def console_delete_last_line(self):
        self.console.text = "\n".join(self.console.text.split("\n")[:-1])

    @mainthread
    def _update_skip_value(self):
        if self.blog2epub_settings.data.limit and int(self.blog2epub_settings.data.limit) > 0:
            skip = int(self.blog2epub_settings.data.limit)
            if self.blog2epub_settings.data.skip and int(self.blog2epub_settings.data.skip) > 0:
                skip += int(self.blog2epub_settings.data.skip)
            self.skip_entry.text = str(skip)
            self.save_settings()

    def _get_url(self):
        if urllib.parse.urlparse(self.url_entry.text):
            port, self.url_entry.text = prepare_port_and_url(self.url_entry.text)
            return self.url_entry.text
        raise BadUrlException("Blog url is not valid.")

    def _download_ebook(self, blog2epub: Blog2Epub):
        blog2epub.download()
        self._enable_download_button()
        if len(blog2epub.crawler.articles) > 0:
            self.tab_select.disabled = False
            self._update_articles_data(blog2epub.crawler.articles)
            self.articles_table.update_row_data(self.articles_table, self._get_articles_rows())
            self.blog2epub_settings.data.language = blog2epub.crawler.language
            self.ebook_data = blog2epub.crawler.get_book_data()
            self.articles_table.update_row_data(self.articles_table, self._get_articles_rows())
            self._update_tab_generate()
        if not blog2epub.crawler.cancelled:
            self.interface.print("Download completed.")
            if len(blog2epub.crawler.articles) > 0:
                self._update_skip_value()
            if platform != "android":
                notification.notify(
                    title="blog2epub - download completed",
                    message=f"{blog2epub.crawler.url}",
                    timeout=2,
                )
            self._switch_tab("Select")

    @mainthread
    def _switch_tab(self, tab_title: str):
        self.tabs.switch_tab(name_tab=tab_title, search_by="title")

    def _get_articles_to_save(self) -> list[ArticleModel]:
        articles_to_save = []
        for x in range(0, len(self.articles_data)):
            if self.articles_data[x][0]:
                articles_to_save.append(self.ebook_data.articles[x])
        return articles_to_save

    def _get_platform_name(self) -> str:
        platform_name = ""
        if platform == "android":
            platform_name = "Android"
        if platform == "win":
            platform_name = "Windows"
        if platform == "macos":
            platform_name = "MacOS"
        if platform == "linux":
            platform_name = "Linux"
        if platform_name:
            return f"on {platform_name}"
        return platform_name

    def generate(self, *args, **kwargs):
        if not self._generate_lock:
            self._generate_lock = self.generate_button.disabled = True
            if self.ebook_data:
                ebook = Book(
                    book_data=self.ebook_data,
                    configuration=self.blog2epub_settings.data,
                    interface=self.interface,
                    destination_folder=self.blog2epub_settings.data.destination_folder,
                    platform_name=self._get_platform_name(),
                )
                ebook.save(self._get_articles_to_save())
                self.popup_success(ebook)
                self._generate_lock = self.generate_button.disabled = False

    def _update_articles_data(self, articles: list):
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

    def download(self, button_instance):
        global USER_DATA_DIR
        self.url_entry.error = False
        self.interface.clear()
        self._disable_download_button()
        self.articles_table.update_row_data(self.articles_table, [])
        self.tab_select.disabled = True
        self.save_settings()
        try:
            self.blog2epub = Blog2Epub(
                url=self._get_url(),
                configuration=self.blog2epub_settings.data,
                cache_folder=USER_DATA_DIR,
                interface=self.interface,
            )
            self.download_thread = Thread(
                target=self._download_ebook,
                kwargs={"blog2epub": self.blog2epub},
            )
            self.download_thread.start()
        except (BadUrlException, urllib.error.URLError):
            self.url_entry.error = True

    def cancel_download(self, *args, **kwargs):
        if self.blog2epub:
            self.blog2epub.crawler.cancelled = True
            while self.blog2epub.crawler.active:
                logging.info("Cancelling download...")
                time.sleep(1)
            self.interface.print("Download cancelled.")
            self._update_tab_generate()

    @mainthread
    def _disable_download_button(self):
        self.download_button_container.remove_widget(self.download_button)
        self.download_button_container.add_widget(self.cancel_button)

    @mainthread
    def _enable_download_button(self):
        self.download_button_container.remove_widget(self.cancel_button)
        self.download_button_container.add_widget(self.download_button)

    def save_settings(self):
        port, self.blog2epub_settings.data.url = prepare_port_and_url(self.url_entry.text)
        self.blog2epub_settings.data.limit = self.limit_entry.text
        self.blog2epub_settings.data.skip = self.skip_entry.text
        self.blog2epub_settings.save()

    @mainthread
    def popup_success(self, ebook: Book):
        self.success(ebook)

    @staticmethod
    def _android_share(file_full_path):
        from jnius import (  # type: ignore
            autoclass,  # type: ignore
            cast,  # type: ignore
        )

        StrictMode = autoclass("android.os.StrictMode")
        StrictMode.disableDeathOnFileUriExposure()
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        File = autoclass("java.io.File")

        epub_file = File(file_full_path)
        epub_uri = Uri.fromFile(epub_file)

        view_intent = Intent(Intent.ACTION_VIEW)
        view_intent.setDataAndType(epub_uri, "application/epub+zip")

        current_activity = cast("android.app.Activity", PythonActivity.mActivity)
        current_activity.startActivity(view_intent)

    def _open_epub(self, file_full_path, inst):
        self.interface.print(f"Opening file: {file_full_path} ({platform})")
        if platform == "win":
            os.startfile(file_full_path)  # type: ignore
        elif platform == "android":
            self._android_share(file_full_path)
        else:
            opener = "open" if sys.platform == "osx" else "xdg-open"
            subprocess.call([opener, file_full_path])

    def success(self, ebook: Book):
        success_content = MDBoxLayout(orientation="vertical")
        epub_cover_image_widget = MDBoxLayout(
            padding=sp(10),
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

        buttons_row = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.1),
            spacing=sp(10),
        )
        buttons_row.add_widget(
            MDRoundFlatIconButton(
                text="Read epub",
                icon="book-open-variant",
                font_size=sp(16),
                font_name=UI_FONT_NAME,
                size_hint=(0.5, 1),
                on_press=partial(self._open_epub, ebook.file_full_path),
            )
        )
        success_content.add_widget(buttons_row)

        success_popup = Popup(
            title="Ebook generated successfully:",
            title_size=sp(20),
            title_font=UI_FONT_NAME,
            content=success_content,
            size_hint=(0.8, 0.8),
        )
        success_popup.open()


class KivyInterface(EmptyInterface):
    def __init__(self, console_output, console_clear, console_delete_last_line):
        self.console_output = console_output
        self.console_clear = console_clear
        self.console_delete_last_line = console_delete_last_line

    def print(self, text: str, end: str = "\n"):
        if len(text) > 1:
            logging.info(text)
        self.console_output(text, end)

    def delete_line(self):
        self.console_delete_last_line()

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
        logging.debug(f"Metrics.dpi_rounded = {Metrics.dpi_rounded}")
        logging.debug(f"Metrics.fontscale = {Metrics.fontscale}")
        if platform == "macos":
            self.icon = asset_path("blog2epub.icns")
        elif platform == "win":
            self.icon = asset_path("blog2epub_256px.png")
        else:
            self.icon = asset_path("blog2epub.svg")

    @property
    def name(self):
        """This is workaround for creating user dir named  "../blog2epub" instead "/blog2epubkivy"."""
        self._app_name = "blog2epub"
        return self._app_name

    def build(self):
        global USER_DATA_DIR
        USER_DATA_DIR = self.user_data_dir
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        Window.resizable = False
        if platform != "android":
            Window.size = (sp(800), sp(600))
        return Blog2EpubKivyWindow()


def main():
    Blog2EpubKivy().run()


if __name__ == "__main__":
    main()
