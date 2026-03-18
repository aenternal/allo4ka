import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ResponseFragments, ResponseTemplate


async def build_response(session: AsyncSession, response_id: int | None = None) -> str:
    if response_id is not None:
        template = await session.get(ResponseTemplate, response_id)
        if template:
            return template.text

    rows = (await session.execute(select(ResponseFragments))).scalars().all()
    if not rows:
        return "Пожалуйста, соблюдай правила общения."

    row = random.choice(rows)
    return f"{row.part1}{row.part2}{row.part3}{row.part4}"
