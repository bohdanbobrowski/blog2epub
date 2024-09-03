import os
from pathlib import Path
from typing import Optional

import yaml

from blog2epub.models.configuration import ConfigurationModel


class Blog2EpubSettings:
    def __init__(self):
        self.path = os.path.join(str(Path.home()), ".blog2epub")
        self._prepare_path()
        self.fname = os.path.join(self.path, "blog2epub.yml")
        self.data: ConfigurationModel = self._read()

    def _prepare_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _read(self) -> ConfigurationModel:
        data = ConfigurationModel()
        if not os.path.isfile(self.fname):
            self.save(data)
        else:
            with open(self.fname, "rb") as stream:
                data_in_file = yaml.safe_load(stream)
            data = ConfigurationModel(**data_in_file)
        return data

    def _save_history(self, data: ConfigurationModel) -> ConfigurationModel:
        if data.url and data.url not in data.history:
            data.history.append(data.url)
            sorted(data.history)
        return data

    def save(self, data: Optional[ConfigurationModel] = None):
        if data is None:
            data = self.data
        data = self._save_history(data)
        with open(self.fname, "w") as outfile:
            yaml.dump(data.model_dump(), outfile, default_flow_style=False)
