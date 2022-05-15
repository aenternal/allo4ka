import asyncio
from random import randint
import time
from config import token
from vkbottle import VoiceMessageUploader
from vkbottle.bot import Bot, Message
from textgen import gen
from voice import wavgen

bot = Bot(token=token)


@bot.on.message(text='<msg>')
async def hygiene(message: Message):
    if randint(1, 5) == 2:
        msg = gen()
        await message.answer(msg)
    elif randint(1, 5) == 3:
        await wavgen()
        time.sleep(10)
        voice_msg = VoiceMessageUploader(bot.api)
        voice = await voice_msg.upload(" ", "test.wav", peer_id=message.peer_id)
        await message.answer('', attachment=voice)




bot.run_forever()
