from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings
from app.db import SessionLocal
from app.services.message_router import route_message
from app.tasks.jobs import generate_voice

settings = get_settings()


dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Бот-модератор запущен.")


@dp.message()
async def on_message(message: Message) -> None:
    if not message.text:
        return

    async with SessionLocal() as session:
        result = await route_message(session, "telegram", message.text)

    if result is None:
        return

    await message.answer(result.response_text)
    if result.should_generate_voice:
        generate_voice.delay(result.response_text)


async def run_telegram() -> None:
    if not settings.telegram_bot_token:
        return
    bot = Bot(token=settings.telegram_bot_token)
    await dp.start_polling(bot)
