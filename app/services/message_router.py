from dataclasses import dataclass

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trigger
from app.services.response_builder import build_response


@dataclass(slots=True)
class RouteResult:
    response_text: str
    should_generate_voice: bool


async def route_message(session: AsyncSession, platform: str, text: str) -> RouteResult | None:
    stmt = select(Trigger).where(
        Trigger.is_active.is_(True),
        or_(Trigger.platform == platform, Trigger.platform == "all"),
    )
    triggers = (await session.execute(stmt)).scalars().all()

    lowered = text.lower()
    for trigger in triggers:
        if trigger.pattern.lower() in lowered:
            response = await build_response(session, trigger.response_id)
            return RouteResult(response_text=response, should_generate_voice=True)

    return None
