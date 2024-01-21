from enum import Enum


class Event(Enum):
    message_received = "message_received"
    command_received = "command_received"
    callback_received = "callback_received"
    sign_in = "sign_in"
    sign_up = "sign_up"
    menu_finished = "menu_finished"
