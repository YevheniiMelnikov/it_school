from pathlib import Path

DB_NAME = "sqlite:///database.db"
BOT_TOKEN = (
    "6983921159:AAGwzjL-qS3nzlGam-C-zRTWIgCgOuWrA0I"  # TODO: HIDE SENSITIVE DATA
)
MESSAGES = {
    "messages": "bot/texts/messages.yml",
    "buttons": "bot/texts/buttons.yml",
}
CONFIG_PATH = Path(__file__).parent / "bot" / "config"
IMAGE_PATH = Path(__file__).parent / "bot" / "images"
