import asyncio
from random import randint
import time
from config import token
from vkbottle import VoiceMessageUploader
from vkbottle.bot import Bot, Message
from textgen import gen
from voice import wavgen
import os

bot = Bot(token=token)


@bot.on.message(text='<msg>')
async def hygiene(m: Message):
    if randint(1, 5) == 2:
        await textonator(m)
    elif randint(1, 5) == 3:
        main_loop.create_task(voicenator(m))


async def voicenator(m: Message):
    await wavgen()
    await asyncio.sleep(10)
    if os.path.isfile('test.wav'):
        voice_msg = VoiceMessageUploader(bot.api)
        voice = await voice_msg.upload(" ", "test.wav", peer_id=m.peer_id)
        await m.answer('', attachment=voice)
        os.remove('test.wav')
    else:
        pass


async def textonator(m: Message):
    msg = await gen()
    await m.answer(msg)


main_loop = asyncio.get_event_loop()

bot.run_forever()
