import os
from lib.utils import read_json, write_to_json


class Settings():
    def __init__(self):
        self.root_path = os.path.dirname(__file__)

        self.config_path = os.path.join(self.root_path, "config.json")
        self.config = read_json(self.config_path)

    def get_config(self):
        return read_json(self.config_path)

    def update_config(self, data):
        return write_to_json(self.config_path, data)
