import asyncio

from app.db import SessionLocal
from app.services.tts import find_cached_audio, save_audio_cache, synthesize_to_file
from app.tasks.celery_app import celery_app


@celery_app.task(name="generate_voice")
def generate_voice(text: str) -> str:
    return asyncio.run(_generate_voice_async(text))


async def _generate_voice_async(text: str) -> str:
    async with SessionLocal() as session:
        cached = await find_cached_audio(session, text)
        if cached:
            return cached

        path = synthesize_to_file(text)
        await save_audio_cache(session, text, path)
        return path
