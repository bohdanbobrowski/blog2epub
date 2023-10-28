import os
from pathlib import Path
from typing import Dict

import yaml


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
        return {"url": "", "limit": "", "skip": "", "history": []}

    def _save_history(self):
        if self._data["url"] and self._data["url"] not in self._data["history"]:
            self._data["history"].append(self._data["url"])
            sorted(self._data["history"])

    def save(self):
        self._save_history()
        with open(self.fname, "w") as outfile:
            yaml.dump(self._data, outfile, default_flow_style=False)

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        if key in self._data:
            return self._data[key]
        else:
            return None

SETTINGS = Blog2EpubSettings()