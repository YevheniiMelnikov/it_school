import asyncio

from bot.storage import Storage
from bot.telegram import TelegramBot
from bot.views import MainView
from settings import BOT_TOKEN, DB_NAME


def main():
    db = Storage(db_name=DB_NAME)
    main_view = MainView(db)
    bot = TelegramBot(BOT_TOKEN, db, main_view)
    asyncio.run(bot.start_polling())


if __name__ == "__main__":
    main()
