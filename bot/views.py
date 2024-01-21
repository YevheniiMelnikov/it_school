import re

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.images.images import img_1, img_2, img_3
from bot.logger import logger
from bot.resources.resource_manager import (
    ButtonText,
    MessageText,
    ResourceManager,
    ResourceType,
)
from bot.storage import Storage


class MainView:
    def __init__(self, db: Storage):
        self.db = db
        self.resource_manager = ResourceManager()
        self.selected_answers = []
        self.questionary_fields = {}

    async def show_quiz(self, message: Message) -> None:
        await self.show_step(
            message,
            [ButtonText.option_1_1, ButtonText.option_1_2, ButtonText.option_1_3],
            MessageText.question_1,
            img_1,
        )
        await self.show_step(
            message,
            [ButtonText.option_2_1, ButtonText.option_2_2, ButtonText.option_2_3],
            MessageText.question_2,
            img_2,
        )
        await self.show_step(
            message,
            [ButtonText.option_3_1, ButtonText.option_3_2, ButtonText.option_3_3],
            MessageText.question_3,
            img_3,
        )

    async def show_step(
        self,
        message: Message,
        keys: list[ResourceType],
        question_text: MessageText,
        image: FSInputFile,
    ) -> None:
        builder = InlineKeyboardBuilder()
        button_texts = self.resource_manager.get_button_list(keys)
        for button_text in button_texts:
            builder.row(
                InlineKeyboardButton(text=button_text, callback_data=button_text)
            )
        kb = builder.as_markup()
        await message.answer_photo(
            photo=image,
            caption=self.resource_manager.get_message_text(question_text),
            reply_markup=kb,
        )

    async def request_contact(self, message: Message) -> None:
        share_contact_button = [
            KeyboardButton(
                text=self.resource_manager.get_button_text(ButtonText.share_contact),
                request_contact=True,
            )
        ]
        keyboard = ReplyKeyboardMarkup(
            keyboard=[share_contact_button],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            self.resource_manager.get_message_text(MessageText.share_contact),
            reply_markup=keyboard,
        )

    async def send_start_keyboard(self, message: Message) -> None:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text=self.resource_manager.get_button_text(ButtonText.start)
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            self.resource_manager.get_message_text(MessageText.start),
            reply_markup=keyboard,
        )

    async def process_quiz_answer(self, callback: CallbackQuery) -> None:
        self.selected_answers.append(callback.data)
        if await self.is_correct(callback.data):
            self.db.give_plus_five(callback.from_user.id)

    async def is_correct(self, answer: str) -> bool:
        correct_answers = self.resource_manager.get_button_list(
            [ButtonText.option_1_3, ButtonText.option_2_2, ButtonText.option_3_2]
        )
        return answer in correct_answers

    async def process_user_info(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        match data.get("current_step"):
            case 0:
                name = message.text
                self.questionary_fields["name"] = name
                await state.set_data({"current_step": 1})
            case 1:
                phone = message.contact.phone_number
                self.questionary_fields["phone"] = phone
                await state.set_data({"current_step": 2})
            case 2:
                email = message.text
                if not email:
                    await message.answer(
                        self.resource_manager.get_message_text(
                            MessageText.invalid_email
                        )
                    )
                    return

                if not await self.email_is_valid(email):
                    await message.answer(
                        self.resource_manager.get_message_text(
                            MessageText.invalid_email
                        )
                    )
                    return

                await message.answer(
                    self.resource_manager.get_message_text(
                        MessageText.successful_registration
                    )
                )

                self.questionary_fields["email"] = email
                self.db.update_user_data(message.from_user.id, self.questionary_fields)

                await state.clear()
                logger.info(f"User {message.from_user.id} registered")

    @staticmethod
    async def email_is_valid(email: str) -> bool:
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return bool(re.match(email_pattern, email))
