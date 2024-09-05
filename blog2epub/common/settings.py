import os
from typing import Optional

import yaml

from blog2epub.models.configuration import ConfigurationModel


class Blog2EpubSettings:
    def __init__(self, path: str):
        self.path = path
        self._prepare_path()
        self.settings_file = os.path.join(self.path, "blog2epub.yml")
        self.data: ConfigurationModel = self._read()

    def _prepare_path(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def _read(self) -> ConfigurationModel:
        data = ConfigurationModel()
        if not os.path.isfile(self.settings_file):
            self.save(data)
        else:
            with open(self.settings_file, "rb") as stream:
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
        with open(self.settings_file, "w") as outfile:
            yaml.dump(data.model_dump(), outfile, default_flow_style=False)
