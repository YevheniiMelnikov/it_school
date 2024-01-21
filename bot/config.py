import os

import yaml


class BaseConfig:
    def __init__(self):
        self.config_file_path = self.get_config_file_path()
        self.config_data = self.load_config()

    @staticmethod
    def get_config_file_path() -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "config.yml")

    def load_config(self) -> dict:
        with open(self.config_file_path, "r", encoding="utf-8") as file:
            config_data = yaml.safe_load(file)
        return config_data

    @property
    def config(self) -> dict:
        return self.config_data
