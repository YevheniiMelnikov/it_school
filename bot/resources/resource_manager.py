from enum import Enum, auto

import yaml

from bot.config import BaseConfig


class MessageText(Enum):
    start = auto()
    are_you_here = auto()
    share_contact = auto()
    enter_email = auto()
    enter_name = auto()
    registration_completed = auto()
    quiz_completed = auto()
    question_1 = auto()
    question_2 = auto()
    question_3 = auto()
    answer_accepted = auto()
    already_passed = auto()
    questionary = auto()
    invalid_email = auto()
    successful_registration = auto()
    get_discount = auto()
    complete_registration = auto()


class ButtonText(Enum):
    option_1_1 = auto()
    option_1_2 = auto()
    option_1_3 = auto()
    option_2_1 = auto()
    option_2_2 = auto()
    option_2_3 = auto()
    option_3_1 = auto()
    option_3_2 = auto()
    option_3_3 = auto()
    share_contact = auto()
    start = auto()


ResourceType = str | MessageText | ButtonText


class ResourceManager:
    def __init__(self):
        self.config = self.config = BaseConfig().config
        self.messages = self.load_yaml(self.config["paths"]["messages"])
        self.buttons = self.load_yaml(self.config["paths"]["buttons"])

    @staticmethod
    def load_yaml(file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return data

    def get_message_text(
        self, key: ResourceType, lang: str | None = "ru"
    ) -> str | None:
        if key.name in self.messages:
            return self.messages[key.name].get(lang)
        else:
            raise ValueError(f"Key {key.name} not found in messages.yaml")

    def get_button_text(self, key: ResourceType, lang: str | None = "ru") -> str | None:
        if key.name in self.buttons:
            return self.buttons[key.name].get(lang)
        else:
            raise ValueError(f"Key {key.name} not found in buttons.yaml")

    def get_button_list(
        self, keys: list[ResourceType], lang: str | None = "ru"
    ) -> list[str | None]:
        return [self.get_button_text(key, lang) for key in keys]
