import asyncio
from random import randint
import torch
import os
import time
from config import token
from vkbottle import VoiceMessageUploader
from vkbottle.bot import Bot, Message
from textgen import text_model

bot = Bot(token=token)


# @bot.on.message(text='<msg>')
# async def hygiene(message: Message):
#     if randint(1, 5) == 2:
#         await message.answer(text_model.make_sentence(tries=100))


@bot.on.message(text='f')
async def voicen(message: Message):
    time.sleep(10)
    voice_msg = VoiceMessageUploader(bot.api)
    voice = await voice_msg.upload(" ", "test.wav", peer_id=message.peer_id)
    await message.answer(attachment=voice)


bot.run_forever()
