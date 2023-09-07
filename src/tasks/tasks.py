import asyncio
from celery import Celery

from config import Config


celery = Celery(__name__)
celery.conf.broker_url = Config.CELERY_BROKER_URL
celery.conf.result_backend = Config.CELERY_RESULT_BACKEND
celery.autodiscover_tasks(force=True)


@celery.task(bind=True, name='withdraw_usdt')
def test():
    pass
