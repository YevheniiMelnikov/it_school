import re

from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           KeyboardButton, Message, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.logger import logger
from bot.storage import Storage
from bot.texts.resource_manager import (ButtonText, MessageText, ResourceType,
                                        translate)
from settings import IMAGE_PATH


class MainView:
    def __init__(self, db: Storage):
        self.db = db

    async def show_quiz(self, message: Message) -> None:
        quiz = self.db.get_quiz_list()[-1]
        for question in quiz.questions:
            keys = [
                f"{quiz.id}.{question.id}.{option['key']}"
                for option in question.options
            ]
            image = FSInputFile(path=str(IMAGE_PATH / question.image))
            await self.show_step(
                message, question.option_buttons, question.message, image, keys
            )

    @staticmethod
    async def show_step(
        message: Message,
        buttons: list[ResourceType],
        question_text: ResourceType,
        image: FSInputFile,
        keys: list[str],
    ) -> None:
        builder = InlineKeyboardBuilder()
        button_texts = [translate(key) for key in buttons]
        for button_text, key in zip(button_texts, keys):
            builder.row(InlineKeyboardButton(text=button_text, callback_data=key))
        kb = builder.as_markup()
        await message.answer_photo(
            photo=image,
            caption=translate(question_text),
            reply_markup=kb,
        )

    @staticmethod
    async def request_contact(message: Message) -> None:
        share_contact_button = [
            KeyboardButton(
                text=translate(ButtonText.share_contact),
                request_contact=True,
            )
        ]
        keyboard = ReplyKeyboardMarkup(
            keyboard=[share_contact_button],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            translate(MessageText.share_contact),
            reply_markup=keyboard,
        )

    @staticmethod
    async def send_start_keyboard(message: Message) -> None:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=translate(ButtonText.start))]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            translate(MessageText.start),
            reply_markup=keyboard,
        )

    async def process_quiz_answer(self, callback: CallbackQuery, user_id: int) -> None:
        quiz_id, question_id, option_key = callback.data.split(".")
        quiz = self.db.get_quiz_list()[-1]
        question = quiz.get_question(int(question_id))
        if question.answer == option_key:
            self.db.give_plus_five(callback.from_user.id)
        self.db.save_answer(int(quiz_id), int(question_id), option_key, user_id)

    async def process_user_info(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        match data.get("current_step"):
            case 0:
                name = message.text
                self.db.update_user_data(message.from_user.id, {"name": name})
                await state.set_data({"current_step": 1})
            case 1:
                phone = message.contact.phone_number
                self.db.update_user_data(message.from_user.id, {"phone": phone})
                await state.set_data({"current_step": 2})
            case 2:
                email = message.text
                if not email:
                    await message.answer(translate(MessageText.invalid_email))
                    return

                if not await self.email_is_valid(email):
                    await message.answer(translate(MessageText.invalid_email))
                    return
                self.db.update_user_data(message.from_user.id, {"email": email})

                await message.answer(translate(MessageText.successful_registration))
                await state.clear()
                logger.info(f"User {message.from_user.id} registered")

    @staticmethod
    async def email_is_valid(email: str) -> bool:
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return bool(re.match(email_pattern, email))
