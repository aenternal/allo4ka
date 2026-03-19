from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Trigger(Base):
    __tablename__ = "triggers"
    __table_args__ = (UniqueConstraint("platform", "pattern", name="uq_triggers_platform_pattern"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(32), default="all", index=True)
    pattern: Mapped[str] = mapped_column(String(255), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ResponseTemplate(Base):
    __tablename__ = "responses"
    __table_args__ = (UniqueConstraint("text", name="uq_responses_text"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    voice_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class TriggerResponseLink(Base):
    __tablename__ = "trigger_response_links"
    __table_args__ = (UniqueConstraint("trigger_id", "response_id", name="uq_trigger_response_link"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trigger_id: Mapped[int] = mapped_column(ForeignKey("triggers.id", ondelete="CASCADE"), index=True)
    response_id: Mapped[int] = mapped_column(ForeignKey("responses.id", ondelete="CASCADE"), index=True)


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
