from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Trigger(Base):
    __tablename__ = "triggers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(32), default="all", index=True)
    pattern: Mapped[str] = mapped_column(String(255), index=True)
    response_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ResponseTemplate(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    voice_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class ResponseFragments(Base):
    __tablename__ = "response_fragments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    part1: Mapped[str] = mapped_column(String(255))
    part2: Mapped[str] = mapped_column(String(255))
    part3: Mapped[str] = mapped_column(String(255))
    part4: Mapped[str] = mapped_column(String(255))


class AudioCache(Base):
    __tablename__ = "audio_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    file_path: Mapped[str] = mapped_column(String(512))
