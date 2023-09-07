from dotenv import load_dotenv, find_dotenv
from os import environ


load_dotenv(find_dotenv())


class Config:
    
    BEARER = environ.get('ALLO4KA_API_KEY')

    BOT_TOKEN = environ.get('TOKEN')
    CHAT_ID = environ.get('CHAT_ID')
    
    REDIS_HOST = environ.get('REDIS_HOST')
    REDIS_PORT = environ.get('REDIS_PORT')
    
    CELERY_BROKER_URL = environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = environ.get('CELERY_RESULT_BACKEND')
    