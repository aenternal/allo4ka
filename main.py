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
async def hygiene(m: Message):
    if randint(1, 5) == 2:
        await textonator(m)
    elif randint(1, 5) == 3:
        await voicenator(m)


async def voicenator(m: Message):
    await wavgen()
    time.sleep(10)
    voice_msg = VoiceMessageUploader(bot.api)
    voice = await voice_msg.upload(" ", "test.wav", peer_id=m.peer_id)
    await m.answer('', attachment=voice)


async def textonator(m: Message):
    msg = gen()
    await m.answer(msg)


bot.run_forever()
