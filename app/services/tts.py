import hashlib
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import AudioCache

settings = get_settings()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def find_cached_audio(session: AsyncSession, text: str) -> str | None:
    text_hash = hash_text(text)
    stmt = select(AudioCache).where(AudioCache.text_hash == text_hash)
    entry = (await session.execute(stmt)).scalar_one_or_none()
    if entry and os.path.exists(entry.file_path):
        return entry.file_path
    return None


async def save_audio_cache(session: AsyncSession, text: str, file_path: str) -> None:
    text_hash = hash_text(text)
    session.add(AudioCache(text_hash=text_hash, text=text, file_path=file_path))
    await session.commit()


def synthesize_to_file(text: str) -> str:
    """
    Заглушка TTS.
    Здесь можно подключить silero, gTTS, ElevenLabs и т.д.
    """
    Path(settings.tts_output_dir).mkdir(parents=True, exist_ok=True)
    target = Path(settings.tts_output_dir) / f"{hash_text(text)}.wav"
    if not target.exists():
        target.write_bytes(b"RIFF....WAVEfmt ")
    return str(target)
