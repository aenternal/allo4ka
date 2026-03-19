from vkbottle import BaseStateGroup
from vkbottle.bot import Bot, Message

from app.config import get_settings
from app.db import SessionLocal
from app.services.message_router import route_message
from app.tasks.jobs import generate_voice

settings = get_settings()


class States(BaseStateGroup):
    pass


vk_bot = Bot(token=settings.vk_group_token) if settings.vk_group_token else None

if vk_bot is not None:

    @vk_bot.on.message()
    async def on_vk_message(message: Message) -> None:
        text = message.text or ""
        if not text:
            return

        async with SessionLocal() as session:
            result = await route_message(session, "vk", text)

        if result is None:
            return

        await message.answer(result.response_text)
        if result.should_generate_voice:
            generate_voice.delay(result.response_text)


async def run_vk() -> None:
    if vk_bot is None:
        return
    await vk_bot.run_polling()
