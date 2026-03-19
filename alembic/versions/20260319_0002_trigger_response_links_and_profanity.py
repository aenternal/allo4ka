"""normalize trigger-response relations

Revision ID: 20260319_0002
Revises: 20260318_0001
Create Date: 2026-03-19 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260319_0002"
down_revision = "20260318_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trigger_response_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trigger_id", sa.Integer(), sa.ForeignKey("triggers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("response_id", sa.Integer(), sa.ForeignKey("responses.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_trigger_response_links_trigger_id", "trigger_response_links", ["trigger_id"])
    op.create_index("ix_trigger_response_links_response_id", "trigger_response_links", ["response_id"])
    op.create_unique_constraint(
        "uq_trigger_response_link",
        "trigger_response_links",
        ["trigger_id", "response_id"],
    )

    bind = op.get_bind()
    trigger_rows = bind.execute(sa.text("SELECT id, response_id FROM triggers WHERE response_id IS NOT NULL")).fetchall()
    for row in trigger_rows:
        bind.execute(
            sa.text(
                """
                INSERT INTO trigger_response_links (trigger_id, response_id)
                VALUES (:trigger_id, :response_id)
                ON CONFLICT DO NOTHING
                """
            ),
            {"trigger_id": row.id, "response_id": row.response_id},
        )

    with op.batch_alter_table("responses") as batch_op:
        batch_op.create_unique_constraint("uq_responses_text", ["text"])

    with op.batch_alter_table("triggers") as batch_op:
        batch_op.create_unique_constraint("uq_triggers_platform_pattern", ["platform", "pattern"])
        batch_op.drop_column("response_id")


def downgrade() -> None:
    with op.batch_alter_table("triggers") as batch_op:
        batch_op.add_column(sa.Column("response_id", sa.Integer(), nullable=True))

    bind = op.get_bind()
    link_rows = bind.execute(
        sa.text(
            """
            SELECT trigger_id, MIN(response_id) AS response_id
            FROM trigger_response_links
            GROUP BY trigger_id
            """
        )
    ).fetchall()
    for row in link_rows:
        bind.execute(
            sa.text("UPDATE triggers SET response_id = :response_id WHERE id = :trigger_id"),
            {"trigger_id": row.trigger_id, "response_id": row.response_id},
        )

    with op.batch_alter_table("triggers") as batch_op:
        batch_op.drop_constraint("uq_triggers_platform_pattern", type_="unique")

    with op.batch_alter_table("responses") as batch_op:
        batch_op.drop_constraint("uq_responses_text", type_="unique")

    op.drop_constraint("uq_trigger_response_link", "trigger_response_links", type_="unique")
    op.drop_index("ix_trigger_response_links_response_id", table_name="trigger_response_links")
    op.drop_index("ix_trigger_response_links_trigger_id", table_name="trigger_response_links")
    op.drop_table("trigger_response_links")
