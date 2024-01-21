import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.logger import logger
from bot.resources.resource_manager import ButtonText, MessageText, ResourceManager


class TelegramBot:
    def __init__(self, token, database, main_view):
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.active_timers = set()
        self.db = database
        self.resource_manager = ResourceManager()
        self.main_view = main_view
        self.active_timers_lock = asyncio.Lock()
        self.setup_handlers()

    def setup_handlers(self) -> None:
        self.dp.message(CommandStart())(self.command_start_handler)
        self.dp.callback_query()(self.callback_handler)
        self.dp.message()(self.message_handler)

    async def command_start_handler(self, message: Message) -> None:
        user_id = message.from_user.id

        async with self.active_timers_lock:
            if user_id in self.active_timers:
                self.active_timers.discard(user_id)

        user = self.db.get_user_by_id(user_id)

        if user:
            if user.test_passed:
                await message.answer(
                    self.resource_manager.get_message_text(MessageText.already_passed)
                )
                state = self.dp.fsm.get_context(self.bot, message.chat.id, user_id)
                await self.start_questionary(user_id, state)
            else:
                await self.main_view.send_start_keyboard(message)
                await asyncio.create_task(self.start_timer(user_id, "start"))
        else:
            self.db.add_user(user_id)
            await self.main_view.send_start_keyboard(message)
            await asyncio.create_task(self.start_timer(user_id, "start"))

    async def start_quiz(self, message: Message, user_id: int) -> None:
        await self.main_view.show_quiz(message)
        await asyncio.create_task(self.start_timer(user_id, "quiz"))

    async def start_timer(self, user_id: int, timer_type: str) -> None:
        timer_config = {
            "start": {"message": MessageText.are_you_here, "timeout": 10},
            "quiz": {"message": MessageText.get_discount, "timeout": 300},
            "questionary": {
                "message": MessageText.complete_registration,
                "timeout": 300,
            },
        }

        if timer_type not in timer_config:
            raise ValueError("Invalid timer type")

        config = timer_config[timer_type]
        message = self.resource_manager.get_message_text(config["message"])
        timeout = config["timeout"]

        self.active_timers.add(user_id)
        logger.info(f"Timer started for user {user_id}")

        try:
            await asyncio.wait_for(
                self.wait_for_user_activity(user_id), timeout=timeout
            )
        except asyncio.TimeoutError:
            async with self.active_timers_lock:
                if user_id in self.active_timers and self.db.check_user_existence(
                    user_id
                ):
                    await self.bot.send_message(user_id, message)

    async def wait_for_user_activity(self, user_id: int) -> None:
        while user_id in self.active_timers:
            await asyncio.sleep(1)

    async def callback_handler(self, callback: CallbackQuery) -> None:
        user_id = callback.from_user.id
        logger.info(f"User {user_id} answered: {callback.data}")
        state = self.dp.fsm.get_context(self.bot, callback.message.chat.id, user_id)

        async with self.active_timers_lock:
            if user_id in self.active_timers:
                self.active_timers.discard(user_id)
                logger.info(f"Timer stopped for user {user_id}")
        await self.main_view.process_quiz_answer(callback)
        await self.bot.answer_callback_query(
            callback.id,
            self.resource_manager.get_message_text(MessageText.answer_accepted),
        )
        await callback.message.delete()

        if len(self.main_view.selected_answers) == 3:
            await self.quiz_completed(user_id, state)

    async def message_handler(self, message: Message) -> None:
        user_id = message.from_user.id
        logger.info(f"Message from user {user_id}: {message.text}")
        async with self.active_timers_lock:
            if user_id in self.active_timers:
                self.active_timers.discard(user_id)
                logger.info(f"Timer stopped for user {user_id}")
        if message.text == self.resource_manager.get_button_text(ButtonText.start):
            await self.start_quiz(message, user_id)
        state = self.dp.fsm.get_context(self.bot, message.chat.id, user_id)
        data = await state.get_data()
        current_step = data.get("current_step")
        match current_step:
            case 0:
                await self.main_view.request_contact(message)
            case 1:
                await self.bot.send_message(
                    user_id,
                    self.resource_manager.get_message_text(MessageText.enter_email),
                )
        await self.main_view.process_user_info(message, state)

    async def quiz_completed(self, user_id: int, state: FSMContext) -> None:
        self.db.update_user_data(user_id, {"test_passed": True})
        discount = self.db.get_user_by_id(user_id).discount
        await self.bot.send_message(
            user_id,
            self.resource_manager.get_message_text(MessageText.quiz_completed).format(
                discount=discount
            ),
        )
        assert self.db.get_user_by_id(user_id).test_passed
        await self.bot.send_message(
            user_id, self.resource_manager.get_message_text(MessageText.questionary)
        )
        await self.start_questionary(user_id, state)

    async def start_questionary(self, user_id: int, state: FSMContext = None) -> None:
        await state.set_data({"current_step": 0})
        await self.bot.send_message(
            user_id, self.resource_manager.get_message_text(MessageText.enter_name)
        )
        await asyncio.create_task(self.start_timer(user_id, "questionary"))

    async def start_polling(self) -> None:
        try:
            await self.dp.start_polling(self.bot)
            logger.info("Telegram bot started")
        except Exception as e:
            logger.exception(f"Error: {e}")
        finally:
            self.db.close()
