import asyncio
import os
from celery import Celery
from vkbottle import VoiceMessageUploader
from vkbottle.bot import Message


from src.config import Config
from src.service import wavgen


celery = Celery(__name__)
celery.conf.broker_url = Config.CELERY_BROKER_URL
celery.conf.result_backend = Config.CELERY_RESULT_BACKEND
celery.autodiscover_tasks(force=True)


@celery.task(bind=True, name='send_voice_message')
def send_voice_message(message: Message, bot):
    wavgen('Мяу-мяу, я милая Аллочка-киса! Няяя!')
    while not os.path.isfile('src/uploads/voice_messages/test.wav'):
        pass
    voice_msg = VoiceMessageUploader(bot.api)
    voice = asyncio.run(voice_msg.upload(" ", "test.wav", peer_id=message.peer_id))
    asyncio.run(message.answer('', attachment=voice))
    os.remove('src/uploads/voice_messages/test.wav')
    asyncio.run(message.answer())
