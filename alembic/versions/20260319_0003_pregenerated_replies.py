"""add pregenerated replies table

Revision ID: 20260319_0003
Revises: 20260319_0002
Create Date: 2026-03-19 00:30:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260319_0003"
down_revision = "20260319_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pre_generated_replies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("audio_path", sa.String(length=512), nullable=True),
        sa.Column("voice_ready", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_unique_constraint(
        "uq_pre_generated_replies_text",
        "pre_generated_replies",
        ["text"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_pre_generated_replies_text", "pre_generated_replies", type_="unique")
    op.drop_table("pre_generated_replies")
