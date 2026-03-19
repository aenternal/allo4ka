from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AudioCache, ResponseTemplate
from app.services.response_builder import build_response
from app.services.tts import find_cached_audio, save_audio_cache, synthesize_to_file


@dataclass(slots=True)
class VoicePreGenerationResult:
    created: int
    cached_total: int


async def pregenerate_voice_cache(
    session: AsyncSession,
    fragment_count: int,
) -> VoicePreGenerationResult:
    texts: set[str] = set()

    stored_responses = (
        await session.execute(select(ResponseTemplate.text).where(ResponseTemplate.voice_enabled.is_(True)))
    ).scalars().all()
    texts.update(stored_responses)

    for _ in range(max(fragment_count, 0)):
        texts.add(await build_response(session))

    created = 0
    for text in texts:
        cached_audio = await find_cached_audio(session, text)
        if cached_audio is not None:
            continue
        cached_audio = synthesize_to_file(text)
        await save_audio_cache(session, text, cached_audio)
        created += 1

    cached_total = len((await session.execute(select(AudioCache.id))).scalars().all())
    return VoicePreGenerationResult(created=created, cached_total=cached_total)


async def list_audio_cache(session: AsyncSession) -> list[AudioCache]:
    return (await session.execute(select(AudioCache).order_by(AudioCache.id.desc()))).scalars().all()
