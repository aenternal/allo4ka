import asyncio
from random import randint

from config import token
from vkbottle.bot import Bot, Message
from textgen import text_model

bot = Bot(token=token)


# рандомное сообщение о гигиене
@bot.on.message(text='<msg>')
async def hygiene(message: Message):
    if randint(1, 5) == 2:
        await message.answer(text_model.make_sentence(tries=100))
    else:
        pass


bot.run_forever()
