import dataclasses
import os
import random

import yaml

from blog2epub.common.crawler import prepare_port_and_url
from blog2epub.common.globals import VERSION
from blog2epub.models.configuration import ConfigurationModel

example_blogs = [
    "https://19thcentury.wordpress.com",
    "https://archaia-ellada.blogspot.com",
    "https://cyclehistory.wordpress.com",
    "https://historicaltidbits.blogspot.com",
    "https://knippsen.blogspot.com",
    "https://ksgedania.blogspot.com",
    "https://motorbikes.blog",
    "https://nrdblog.cmosnet.eu",
    "https://oldcam.wordpress.com",
    "https://oldcamera.blog",
    "https://python-bloggers.com",
    "https://rocket-garage.blogspot.com",
    "https://starybezpiek.blogspot.com",
    "https://thevictoriancyclist.wordpress.com",
    "https://velosov.blogspot.com",
    "https://vintagebicycle.wordpress.com",
    "https://vowe.net",
    "https://www.blog.homebrewing.pl",
    "https://www.historyoftheancientworld.com",
    "https://www.infolotnicze.pl",
    "https://www.mikeanderson.biz",
    "https://www.nomadicmatt.com",
    "https://www.returnofthecaferacers.com",
    "https://www.szarmant.pl",
]


class Blog2EpubSettings:
    def __init__(self, path: str):
        self.path = path
        self._prepare_path()
        self.settings_file = os.path.join(self.path, "blog2epub.yml")
        self.data: ConfigurationModel = self._read()

    def _prepare_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    @staticmethod
    def _normalise_history(history: list[str]) -> list[str]:
        """Used only when loading configs older than v.1.5.0"""
        output_history = []
        for item in history:
            port, url = prepare_port_and_url(item)
            output_history.append(url)
        output_history = list(set(output_history))
        return output_history

    def _read(self) -> ConfigurationModel:
        data = ConfigurationModel()
        if not os.path.isfile(self.settings_file):
            self.save(data)
        else:
            with open(self.settings_file, "rb") as stream:
                data_in_file = yaml.load(stream, Loader=yaml.Loader)
                if "version" not in data_in_file:
                    data_in_file["version"] = VERSION
                    data_in_file["history"] = self._normalise_history(data_in_file["history"])
            if data_in_file:
                data = ConfigurationModel(**data_in_file)
            else:
                data = ConfigurationModel()
        if data.url == "":
            data.url = "https://blog2epub.blogspot.com" # random.choice(example_blogs)
        return data

    @staticmethod
    def _save_history(data: ConfigurationModel) -> ConfigurationModel:
        if data.url and data.url not in data.history:
            data.history.append(data.url)
            sorted(data.history)
        return data

    def save(self, data: ConfigurationModel | None = None):
        if data is None:
            data = self.data
        data = self._save_history(data)
        with open(self.settings_file, "w") as outfile:
            data_dict = dataclasses.asdict(data)
            yaml.dump(data_dict, outfile, default_flow_style=False)
