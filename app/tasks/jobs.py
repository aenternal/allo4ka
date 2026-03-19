import asyncio

from app.db import SessionLocal
from app.services.pre_generation import pregenerate_voice_cache
from app.services.tts import find_cached_audio, save_audio_cache, synthesize_to_file
from app.tasks.celery_app import celery_app


@celery_app.task(name="generate_voice")
def generate_voice(text: str) -> str:
    return asyncio.run(_generate_voice_async(text))


@celery_app.task(name="pregenerate_voice")
def pregenerate_voice(fragment_count: int = 10) -> dict[str, int]:
    return asyncio.run(_pregenerate_voice_async(fragment_count))


async def _generate_voice_async(text: str) -> str:
    async with SessionLocal() as session:
        cached = await find_cached_audio(session, text)
        if cached:
            return cached

        path = synthesize_to_file(text)
        await save_audio_cache(session, text, path)
        return path


async def _pregenerate_voice_async(fragment_count: int) -> dict[str, int]:
    async with SessionLocal() as session:
        result = await pregenerate_voice_cache(session, fragment_count)
        return {"created": result.created, "cached_total": result.cached_total}
