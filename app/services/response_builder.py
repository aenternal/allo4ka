import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ResponseFragments, ResponseTemplate, TriggerResponseLink


async def build_response(session: AsyncSession, trigger_id: int | None = None) -> str:
    if trigger_id is not None:
        response_ids = (
            await session.execute(
                select(TriggerResponseLink.response_id).where(TriggerResponseLink.trigger_id == trigger_id)
            )
        ).scalars().all()
        if response_ids:
            responses = (
                await session.execute(select(ResponseTemplate).where(ResponseTemplate.id.in_(response_ids)))
            ).scalars().all()
            if responses:
                return random.choice(responses).text

    rows = (await session.execute(select(ResponseFragments))).scalars().all()
    if not rows:
        return "Пожалуйста, соблюдай правила общения."

    row = random.choice(rows)
    return f"{row.part1}{row.part2}{row.part3}{row.part4}"
