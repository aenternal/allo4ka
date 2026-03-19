"""initial schema and seed data

Revision ID: 20260318_0001
Revises: None
Create Date: 2026-03-18 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260318_0001"
down_revision = None
branch_labels = None
depends_on = None


trigger_table = sa.table(
    "triggers",
    sa.column("platform", sa.String(length=32)),
    sa.column("pattern", sa.String(length=255)),
    sa.column("response_id", sa.Integer()),
    sa.column("is_active", sa.Boolean()),
)

response_table = sa.table(
    "responses",
    sa.column("id", sa.Integer()),
    sa.column("text", sa.Text()),
    sa.column("voice_enabled", sa.Boolean()),
)

fragment_table = sa.table(
    "response_fragments",
    sa.column("part1", sa.String(length=255)),
    sa.column("part2", sa.String(length=255)),
    sa.column("part3", sa.String(length=255)),
    sa.column("part4", sa.String(length=255)),
)


def upgrade() -> None:
    op.create_table(
        "triggers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(length=32), nullable=False, server_default="all"),
        sa.Column("pattern", sa.String(length=255), nullable=False),
        sa.Column("response_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_triggers_platform", "triggers", ["platform"])
    op.create_index("ix_triggers_pattern", "triggers", ["pattern"])

    op.create_table(
        "responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("voice_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "response_fragments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part1", sa.String(length=255), nullable=False),
        sa.Column("part2", sa.String(length=255), nullable=False),
        sa.Column("part3", sa.String(length=255), nullable=False),
        sa.Column("part4", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "audio_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text_hash", sa.String(length=64), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
    )
    op.create_index("ix_audio_cache_text_hash", "audio_cache", ["text_hash"], unique=True)

    op.bulk_insert(
        response_table,
        [
            {
                "id": 1,
                "text": "Тормозни, легенда района: ругаться можно и веселее, но лучше всё-таки без пожара в комментариях.",
                "voice_enabled": True,
            },
            {
                "id": 2,
                "text": "Словарь мата у тебя богатый, спору нет, но давай оставим его как музейный экспонат, а не рабочий инструмент.",
                "voice_enabled": True,
            },
        ],
    )

    op.bulk_insert(
        trigger_table,
        [
            {"platform": "all", "pattern": "бля", "response_id": 1, "is_active": True},
            {"platform": "all", "pattern": "сука", "response_id": 2, "is_active": True},
            {"platform": "all", "pattern": "нахуй", "response_id": 1, "is_active": True},
            {"platform": "all", "pattern": "пиздец", "response_id": 2, "is_active": True},
        ],
    )

    op.bulk_insert(
        fragment_table,
        [
            {
                "part1": "Ах ты, блин, карамельный обормот",
                "part2": ", ещё раз сюда ворвёшься с такой бранью",
                "part3": ", я вызову комитет по делам громких слов",
                "part4": ", чемпион по драме районного масштаба!",
            },
            {
                "part1": "Ну ты и лихой балбес с турборежимом",
                "part2": ", продолжишь так фехтовать матюками",
                "part3": ", и даже чайник на кухне попросит пощады",
                "part4": ", герцог словесной катастрофы!",
            },
            {
                "part1": "Ёкарный бабай, артист погорелого театра",
                "part2": ", если опять включишь этот матерный салют",
                "part3": ", я тебе виртуально выдам штраф за шум",
                "part4": ", барон перепалки и суеты!",
            },
            {
                "part1": "Ах ты ж, хрен моржовый",
                "part2": ", ещё одна такая тирада в чатике",
                "part3": ", и сервер сам перекрестится от ужаса",
                "part4": ", принц всратого красноречия!",
            },
            {
                "part1": "Вот ты какой, матерный самурай на минималках",
                "part2": ", повторишь этот номер без аплодисментов",
                "part3": ", и я пришлю тебе грамоту за лишний пафос",
                "part4": ", сын комедийной суматохи!",
            },
            {
                "part1": "Ох ты и шальной пельмень с характером",
                "part2": ", если снова полетят такие словечки",
                "part3": ", я поставлю возле тебя воображаемый цензорский патруль",
                "part4": ", владыка нелепых ругательных симфоний!",
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_audio_cache_text_hash", table_name="audio_cache")
    op.drop_table("audio_cache")
    op.drop_table("response_fragments")
    op.drop_table("responses")
    op.drop_index("ix_triggers_pattern", table_name="triggers")
    op.drop_index("ix_triggers_platform", table_name="triggers")
    op.drop_table("triggers")
