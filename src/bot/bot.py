from src.config import Config
from src.tasks.tasks import send_voice_message
from vkbottle.bot import Message
from overrides import MyBot


bot = MyBot(token=Config.BOT_TOKEN)


@bot.on.message()
async def hygiene(m: Message):
    send_voice_message.delay(message=m, bot=bot)


# async def textonator(m: Message):
#     msg = await gen()
#     await m.answer(msg)

bot.run_forever()
