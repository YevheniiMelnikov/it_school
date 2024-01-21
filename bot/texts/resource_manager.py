from enum import Enum, auto

import yaml

import settings


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

    def __str__(self):
        return f"messages.{self.name}"


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

    def __str__(self):
        return f"buttons.{self.name}"


ResourceType = str | MessageText | ButtonText


class ResourceManager:
    def __init__(self):
        self.messages = self.load_messages()

    def get_text(self, key: ResourceType, lang: str | None = "eng") -> str | None:
        if str(key) in self.messages:
            return self.messages[str(key)][lang]
        else:
            raise ValueError(f"Key {key.name} not found in messages.yaml")

    def load_messages(self) -> dict:
        result = {}
        for type, path in settings.MESSAGES.items():
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            for key, value in data.items():
                result[f"{type}.{key}"] = value
        return result


resource_manager = ResourceManager()


def translate(key: ResourceType, lang: str | None = "ru") -> str:
    return resource_manager.get_text(key, lang)
