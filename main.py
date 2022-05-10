import asyncio

from config import token
from vkbottle.bot import Bot, Message

bot = Bot(token=token)


@bot.on.message(text='Привет')
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer(f'Привет, {users_info[0].first_name}')

bot.run_forever()